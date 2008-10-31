from django import forms
from django.contrib import admin
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext as _, ugettext_lazy
from django.utils.encoding import force_unicode

from django.db import models
from django.http import HttpResponseRedirect
from django.contrib.admin.util import unquote

from pages import settings
from pages.models import Page, PagePermission, Content
from pages.views import details
from pages.utils import get_template_from_request, has_page_add_permission, \
    get_language_from_request

from pages.admin.widgets import RichTextarea, WYMEditor
from pages.admin.utils import get_placeholders
from pages.admin.views import traduction, get_content, valid_targets_list, \
    change_status, modify_content

class PageForm(forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput(),
        help_text=_('The default title'))
    slug = forms.CharField(widget=forms.TextInput(),
        help_text=_('The part of the title that is used in permalinks'))
    language = forms.ChoiceField(choices=settings.PAGE_LANGUAGES,
        help_text=_('The current language of the content fields.'))
    template = forms.ChoiceField(choices=settings.PAGE_TEMPLATES, required=False,
        help_text=_('The template used to render the content.'))

    class Meta:
        model = Page

    def clean_slug(self):
        slug = slugify(self.cleaned_data['slug'])
        # FIX: make unique slugs possible
        # if settings.PAGE_UNIQUE_SLUG_REQUIRED:
        #     if current_page and Page.objects.exclude(pk=current_page.id).filter(slug=slug):
        #         raise forms.ValidationError('Another page with this slug already exists')
        #     if current_page is None and Page.objects.filter(slug=slug):
        #         raise forms.ValidationError('Another page with this slug already exists')
        return slug


class PageAdmin(admin.ModelAdmin):
    form = PageForm
    exclude = ['author', 'parent']
    # these mandatory fields are not versioned
    mandatory_fields = ('title', 'slug', 'template')
    fieldsets = (
        (_('General'), {
            'fields': ('title', 'slug', 'status', 'tags', 'sites'),
            'classes': ('sidebar',),
        }),
        (_('Options'), {
            'fields': ('language', 'template'),
            'classes': ('sidebar', 'clear'),
            'description': _('Note: This page reloads if you change the selection'),
        }),
    )

    def __call__(self, request, url):
        # Delegate to the appropriate method, based on the URL.
        if url is None:
            return self.list_pages(request)
        elif 'traduction' in url:
            page_id, action, language_id = url.split('/')
            return traduction(request, unquote(page_id), unquote(language_id))
        elif 'get-content' in url:
            page_id, action, content_id = url.split('/')
            return get_content(request, unquote(page_id), unquote(content_id))
        elif 'modify-content' in url:
            page_id, action, content_id, language_id = url.split('/')
            return modify_content(request, unquote(page_id),
                                    unquote(content_id), unquote(language_id))
        elif url.endswith('/valid-targets-list'):
            return valid_targets_list(request, unquote(url[:-19]))
        elif url.endswith('/move-page'):
            return self.move_page(request, unquote(url[:-10]))
        elif url.endswith('/change-status'):
            return change_status(request, unquote(url[:-14]))
        return super(PageAdmin, self).__call__(request, url)

    def save_model(self, request, obj, form, change):
        """
        Move the page in the tree if neccesary and save every placeholder
        Content object.
        """
        obj.save()
        language = form.cleaned_data['language']
        target = request.GET.get('target', None)
        position = request.GET.get('position', None)
        if target is not None and position is not None:
            try:
                target = self.model.objects.get(pk=target)
            except self.model.DoesNotExist:
                pass
            else:
                obj.move_to(target, position)

        for mandatory_field in self.mandatory_fields:
            Content.objects.set_or_create_content(obj, language,
                mandatory_field, form.cleaned_data[mandatory_field])

        for placeholder in get_placeholders(request, obj.get_template()):
            if placeholder.name in form.cleaned_data:
                if change:
                    if placeholder.name not in self.mandatory_fields:
                        # we need create a new content if revision is enabled
                        if settings.PAGE_CONTENT_REVISION and placeholder.name \
                                not in settings.PAGE_CONTENT_REVISION_EXCLUDE_LIST:
                            Content.objects.create_content_if_changed(obj, language,
                                placeholder.name, form.cleaned_data[placeholder.name])
                        else:
                            Content.objects.set_or_create_content(obj, language,
                                placeholder.name, form.cleaned_data[placeholder.name])
                else:
                    Content.objects.set_or_create_content(obj, language,
                        placeholder.name, form.cleaned_data[placeholder.name])

    def get_fieldsets(self, request, obj=None):
        """
        Add fieldsets of placeholders to the list of already existing
        fieldsets.
        """
        placeholder_fieldsets = []
        template = get_template_from_request(request, obj)
        for placeholder in get_placeholders(request, template):
            if placeholder.name not in self.mandatory_fields:
                placeholder_fieldsets.append(placeholder.name)

        if self.declared_fieldsets:
            given_fieldsets = list(self.declared_fieldsets)
        else:
            form = self.get_form(request, obj)
            given_fieldsets = [(_('content'), {'fields': form.base_fields.keys()})]
        return given_fieldsets + [(_('content'), {'fields': placeholder_fieldsets})]

    def save_form(self, request, form, change):
        """
        Given a ModelForm return an unsaved instance. ``change`` is True if
        the object is being changed, and False if it's being added.
        """
        instance = super(PageAdmin, self).save_form(request, form, change)
        instance.template = form.cleaned_data['template']
        if not change:
            instance.author = request.user
        return instance

    def get_form(self, request, obj=None, **kwargs):
        """
        Get PageForm for the Page model and modify its fields depending on
        the request.
        """
        form = super(PageAdmin, self).get_form(request, obj, **kwargs)

        language = get_language_from_request(request, obj)
        form.base_fields['language'].initial = force_unicode(language)
        if obj is not None:
            initial_slug = obj.slug(language=language, fallback=False)
            form.base_fields['slug'].initial = initial_slug

        template = get_template_from_request(request, obj)
        template_choices = list(settings.PAGE_TEMPLATES)
        template_choices.insert(0, (settings.DEFAULT_PAGE_TEMPLATE, _('Default template')))
        form.base_fields['template'].choices = template_choices
        form.base_fields['template'].initial = force_unicode(template)

        for placeholder in get_placeholders(request, template):
            if placeholder.widget == 'TextInput':
                widget = forms.TextInput()
            elif placeholder.widget == 'RichTextarea':
                widget = RichTextarea()
            elif placeholder.widget == 'WYMEditor':
                widget = WYMEditor(name=placeholder.name, language=language)
            else:
                widget = forms.Textarea()
            if obj:
                initial = Content.objects.get_content(obj, language,
                                                      placeholder.name)
            else:
                initial = None
            if placeholder.name not in self.mandatory_fields:
                form.base_fields[placeholder.name] = forms.CharField(
                            widget=widget, required=False, initial=initial)
            else:
                form.base_fields[placeholder.name].initial = initial
        return form

    def change_view(self, request, object_id, extra_context=None):
        """
        The 'change' admin view for the Page model.
        """
        try:
            obj = self.model.objects.get(pk=object_id)
        except self.model.DoesNotExist:
            # Don't raise Http404 just yet, because we haven't checked
            # permissions yet. We don't want an unauthenticated user to be able
            # to determine whether a given object exists.
            obj = None
        else:
            template = get_template_from_request(request, obj)
            extra_context = {
                'placeholders': get_placeholders(request, template),
                'language': get_language_from_request(request),
                'traduction_language': settings.PAGE_LANGUAGES,
                'page': obj,
            }
        return super(PageAdmin, self).change_view(request, object_id, extra_context)

    def has_add_permission(self, request):
        """
        Return true if the current user has permission to add a new page.
        """
        if not settings.PAGE_PERMISSION:
            return super(PageAdmin, self).has_add_permission(request)
        else:
            return has_page_add_permission(request)

    def has_change_permission(self, request, obj=None):
        """
        Return true if the current user has permission on the page.
        Return the string 'All' if the user has all rights.
        """
        if settings.PAGE_PERMISSION and obj is not None:
            return obj.has_page_permission(request)
        return super(PageAdmin, self).has_change_permission(request, obj)

    def list_pages(self, request, template_name=None, extra_context=None):
        """
        List root pages
        """
        # HACK: overrides the changelist template and later resets it to None
        if template_name:
            self.change_list_template = template_name
        context = {
            'name': _("page"),
            'pages': Page.objects.root().order_by("tree_id"),
        }
        context.update(extra_context or {})
        change_list = self.changelist_view(request, context)
        self.change_list_template = None
        return change_list

    def move_page(self, request, page_id, extra_context=None):
        """
        Move the page to the requested target, at the given position
        """
        context = {}
        page = Page.objects.get(pk=page_id)

        target = request.POST.get('target', None)
        position = request.POST.get('position', None)
        if target is not None and position is not None:
            try:
                target = self.model.objects.get(pk=target)
            except self.model.DoesNotExist:
                context.update({'error': _('Page could not been moved.')})
            else:
                page.move_to(target, position)
                return self.list_pages(request,
                    template_name='admin/pages/page/change_list_table.html')
        context.update(extra_context or {})
        return HttpResponseRedirect('../../')
admin.site.register(Page, PageAdmin)

class ContentAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'type', 'language', 'page')
    list_filter = ('page',)
    search_fields = ('body',)

#admin.site.register(Content, ContentAdmin)

if settings.PAGE_PERMISSION:
    admin.site.register(PagePermission)

