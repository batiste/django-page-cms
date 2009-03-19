# -*- coding: utf-8 -*-
from os.path import join
from inspect import isclass, getmembers

from django.forms import Widget, TextInput, Textarea, CharField
from django.contrib import admin
from django.utils.translation import ugettext as _, ugettext_lazy
from django.utils.encoding import force_unicode
from django.conf import settings as global_settings
from django.db import models
from django.http import HttpResponseRedirect
from django.contrib.admin.util import unquote

from pages import settings
from pages.models import Page, Content
from pages.utils import get_template_from_request, has_page_add_permission, \
    get_language_from_request

from pages.admin import widgets
from pages.utils import get_placeholders
from pages.admin.forms import PageForm
from pages.admin.utils import get_connected_models
from pages.admin.views import traduction, get_content, sub_menu, \
    change_status, modify_content

class PageAdmin(admin.ModelAdmin):

    form = PageForm
    exclude = ['author', 'parent']
    # these mandatory fields are not versioned
    mandatory_placeholders = ('title', 'slug')
    general_fields = ['title', 'slug', 'status', 'target', 'position']

    # TODO: find solution to do this dynamically
    #if getattr(settings, 'PAGE_USE_SITE_ID'):
    general_fields.append('sites')
    insert_point = general_fields.index('status') + 1

    if settings.PAGE_TAGGING:
        general_fields.insert(insert_point, 'tags')

    # Add support for future dating and expiration based on settings.
    if settings.PAGE_SHOW_END_DATE:
        general_fields.insert(insert_point, 'publication_end_date')
    if settings.PAGE_SHOW_START_DATE:
        general_fields.insert(insert_point, 'publication_date')

    normal_fields = ['language']
    if settings.PAGE_TEMPLATES:
        normal_fields.append('template')

    fieldsets = (
        (_('General'), {
            'fields': general_fields,
            'classes': ('sidebar',),
        }),
        (_('Options'), {
            'fields': normal_fields,
            'classes': ('sidebar', 'clear'),
            'description': _('Note: This page reloads if you change the selection'),
        }),
    )

    class Media:
        css = {
            'all': [join(settings.PAGES_MEDIA_URL, path) for path in (
                'css/rte.css',
                'css/pages.css'
            )]
        }
        js = [join(settings.PAGES_MEDIA_URL, path) for path in (
            'javascript/jquery.js',
            'javascript/jquery.rte.js',
            'javascript/jquery.query.js',
            'javascript/change_form.js',
        )]

    def __call__(self, request, url):
        # Delegate to the appropriate method, based on the URL.
        if url is None:
            return self.list_pages(request)
        elif url == 'jsi18n':
            return self.i18n_javascript(request)
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
        elif url.endswith('/sub-menu'):
            return sub_menu(request, unquote(url[:-9]))
        elif url.endswith('/move-page'):
            return self.move_page(request, unquote(url[:-10]))
        elif url.endswith('/change-status'):
            return change_status(request, unquote(url[:-14]))
        return super(PageAdmin, self).__call__(request, url)

    def i18n_javascript(self, request):
        """
        Displays the i18n JavaScript that the Django admin requires.

        This takes into account the USE_I18N setting. If it's set to False, the
        generated JavaScript will be leaner and faster.
        """
        if global_settings.USE_I18N:
            from django.views.i18n import javascript_catalog
        else:
            from django.views.i18n import null_javascript_catalog as javascript_catalog
        return javascript_catalog(request, packages='pages')

    def save_model(self, request, obj, form, change):
        """
        Move the page in the tree if necessary and save every placeholder
        Content object.
        """

        language = form.cleaned_data['language']
        target = form.data.get('target', None)
        position = form.data.get('position', None)
        obj.save()

        if target and position:
            try:
                target = self.model.objects.get(pk=target)
            except self.model.DoesNotExist:
                pass
            else:
                target.invalidate()
                obj.move_to(target, position)

        for mandatory_placeholder in self.mandatory_placeholders:
            Content.objects.set_or_create_content(obj, language,
                mandatory_placeholder, form.cleaned_data[mandatory_placeholder])

        for placeholder in get_placeholders(obj.get_template()):
            if placeholder.name in form.cleaned_data:
                if change:
                    if placeholder.name not in self.mandatory_placeholders:
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

        obj.invalidate()

    def get_fieldsets(self, request, obj=None):
        """
        Add fieldsets of placeholders to the list of already existing
        fieldsets.
         """
        additional_fieldsets = []

        placeholder_fieldsets = []
        template = get_template_from_request(request, obj)
        for placeholder in get_placeholders(template):
            if placeholder.name not in self.mandatory_placeholders:
                placeholder_fieldsets.append(placeholder.name)

        additional_fieldsets.append((_('Content'), {'fields': placeholder_fieldsets}))

        # deactived for now, create bugs with page with same slug title
        connected_fieldsets = []
        if obj:
            for mod in get_connected_models():
                for field_name, real_field_name, field in mod['fields']:
                    connected_fieldsets.append(field_name)

                additional_fieldsets.append((_('Create a new linked ' +
                    mod['model_name']), {'fields': connected_fieldsets}))

        given_fieldsets = list(self.declared_fieldsets)

        return given_fieldsets + additional_fieldsets

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

    def get_widget(self, request, name, fallback=Textarea):
        """
        Given the request and name of a placeholder return a Widget subclass
        like Textarea or TextInput.
        """
        if name and '.' in name:
            module_name, class_name = name.rsplit('.', 1)
            module = __import__(module_name, {}, {}, [class_name])
            widget = getattr(module, class_name, fallback)
        else:
            widget = dict(getmembers(widgets, isclass)).get(name, fallback)
        if not isinstance(widget(), Widget):
            widget = fallback
        return widget

    def get_form(self, request, obj=None, **kwargs):
        """
        Get PageForm for the Page model and modify its fields depending on
        the request.
        """
        form = super(PageAdmin, self).get_form(request, obj, **kwargs)

        language = get_language_from_request(request, obj)
        form.base_fields['language'].initial = language
        if obj:
            initial_slug = obj.slug(language=language, fallback=False)
            initial_title = obj.title(language=language, fallback=False)
            form.base_fields['slug'].initial = initial_slug
            form.base_fields['title'].initial = initial_title
            form.base_fields['slug'].label = _('Slug')

        template = get_template_from_request(request, obj)
        if settings.PAGE_TEMPLATES:
            template_choices = list(settings.PAGE_TEMPLATES)
            template_choices.insert(0, (settings.DEFAULT_PAGE_TEMPLATE, _('Default template')))
            form.base_fields['template'].choices = template_choices
            form.base_fields['template'].initial = force_unicode(template)

        # handle most of the logic of connected models

        if obj:
            for mod in get_connected_models():
                model = mod['model']
                attributes = {'page': obj.id}
                validate_field = True

                if request.POST:
                    for field_name, real_field_name, field in mod['fields']:
                        if field_name in request.POST and request.POST[field_name]:
                            attributes[real_field_name] = request.POST[field_name]

                    if len(attributes) > 1:
                        connected_form = mod['form'](attributes)
                        if connected_form.is_valid():
                            connected_form.save()
                    else:
                        validate_field = False

                for field_name, real_field_name, field in mod['fields']:
                    form.base_fields[field_name] = field
                    if not validate_field:
                        form.base_fields[field_name].required = False

        for placeholder in get_placeholders(template):
            widget = self.get_widget(request, placeholder.widget)()
            if placeholder.parsed:
                help_text = _('Note: This field is evaluated as template code.')
            else:
                help_text = ""
            name = placeholder.name
            if obj:
                initial = Content.objects.get_content(obj, language, name)
            else:
                initial = None
            if name not in self.mandatory_placeholders:
                form.base_fields[placeholder.name] = CharField(widget=widget,
                    initial=initial, help_text=help_text, required=False)
            else:
                form.base_fields[name].initial = initial
                form.base_fields[name].help_text = help_text

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
                'placeholders': get_placeholders(template),
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

    def has_delete_permission(self, request, obj=None):
        """
        Return true if the current user has permission on the page.
        Return the string 'All' if the user has all rights.
        """
        if settings.PAGE_PERMISSION and obj is not None:
            return obj.has_page_permission(request)
        return super(PageAdmin, self).has_delete_permission(request, obj)

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
            'opts': self.model._meta,
        }
        context.update(extra_context or {})
        change_list = self.changelist_view(request, context)
        self.change_list_template = None
        return change_list

    def move_page(self, request, page_id, extra_context=None):
        """
        Move the page to the requested target, at the given position
        """
        page = Page.objects.get(pk=page_id)

        target = request.POST.get('target', None)
        position = request.POST.get('position', None)
        if target is not None and position is not None:
            try:
                target = self.model.objects.get(pk=target)
            except self.model.DoesNotExist:
                pass
                # TODO: should use the django message system
                # to display this message
                # _('Page could not been moved.')
            else:
                page.invalidate()
                target.invalidate()
                page.move_to(target, position)
                return self.list_pages(request,
                    template_name='admin/pages/page/change_list_table.html')
        return HttpResponseRedirect('../../')

admin.site.register(Page, PageAdmin)

class ContentAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'type', 'language', 'page')
    list_filter = ('page',)
    search_fields = ('body',)

#admin.site.register(Content, ContentAdmin)

if settings.PAGE_PERMISSION:
    from pages.models import PagePermission
    admin.site.register(PagePermission)
