from pages.utils import auto_render
from pages.models import Page, Language, Content
from django.contrib.admin.views.decorators import staff_member_required
from django import newforms as forms
from django.db import models
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.encoding import force_unicode, smart_str
from django.utils.translation import ugettext as _

def get_form(request, dict=None, current_page=None):
    
    if current_page:
        parent_choices = [(page.id, page.slug) for page in Page.objects.exclude(pk=current_page.id)]
    else:
        parent_choices = [(page.id, page.slug) for page in Page.objects.all()]
    parent_choices.insert(0,('','------'))
    language_choices = [(lang.id, lang.name) for lang in Language.objects.all()]
    l = Language.get_from_request(request, current_page)
    import settings
    if hasattr(settings, 'PAGE_TEMPLATES'):
        template_choices = list(settings.PAGE_TEMPLATES)
        template_choices.insert(0,('',_('Inherit')))
    else:
        template_choices = False
    
    class PageForm(forms.Form):
        slug = forms.CharField(widget=forms.TextInput(), required=request.POST) # hackish
        title = forms.CharField(widget=forms.TextInput(), required=request.POST) # hackish
        body = forms.CharField(widget=forms.Textarea(), required=request.POST) # hackish
        language = forms.ChoiceField(choices=language_choices, initial=l.id)
        status = forms.ChoiceField(choices=Page.STATUSES)
        parent = forms.ChoiceField(choices=parent_choices, required=False)
        if template_choices:
            template = forms.ChoiceField(choices=template_choices, required=False)
        
        def clean_slug(self):
            from django.template.defaultfilters import slugify
            if current_page and Page.objects.exclude(pk=current_page.id).filter(slug=slugify(self.cleaned_data['slug'])):
                    raise forms.ValidationError('Another page with this slug already exists')
            return slugify(self.cleaned_data['slug'])
        
        def clean_parent(self):
            if self.cleaned_data['parent'] and current_page and int(self.cleaned_data['parent'])==int(current_page.id):
                raise forms.ValidationError('A page cannot be it\'s parent')
            return self.cleaned_data['parent']
        
    from django.http import QueryDict
    
    if dict and type(dict) is not QueryDict:
        dict['language'] = l.id
        
    if dict:
        return PageForm(dict)
    
    return PageForm()
    
@staff_member_required
@auto_render
def add(request):
    opts = Page._meta
    add = True
    if(request.POST):
        form = get_form(request, request.POST)
        if form.is_valid():
            if form.cleaned_data['parent']:
                parent = Page.objects.get(pk=form.cleaned_data['parent'])
            else:
                parent = None
            status = form.cleaned_data['status']
            slug = form.cleaned_data['slug']
            template = form.cleaned_data.get('template', None)
            page = Page(author=request.user, status=status, parent=parent, slug=slug, template=template)
            page.save()
            language=Language.objects.get(pk=form.cleaned_data['language'])
            Content.set_or_create_content(page, language, 0, form.cleaned_data['title'])
            Content.set_or_create_content(page, language, 1, form.cleaned_data['body'])
            msg = _('The %(name)s "%(obj)s" was added successfully.') % {'name': force_unicode(opts.verbose_name), 'obj': force_unicode(page)}
            request.user.message_set.create(message=msg)
            return HttpResponseRedirect("../")
    else:
        form = get_form(request)

    return 'admin/pages/page/change_form.html', locals()

@staff_member_required
@auto_render
def modify(request, page_id):
    opts = Page._meta
    change = True
    has_absolute_url = True
    page = Page.objects.get(pk=page_id)
    original = page.title()
    if(request.POST):
        form = get_form(request, request.POST, page)
        if form.is_valid():
            language=Language.objects.get(pk=form.cleaned_data['language'])
            Content.set_or_create_content(page, language, 0, form.cleaned_data['title'])
            Content.set_or_create_content(page, language, 1, form.cleaned_data['body'])
            if form.cleaned_data['parent']:
                p = Page.objects.get(pk=form.cleaned_data['parent'])
                # avoid to create a infinite loop
                if p!=page:
                    page.parent = p
            else:
                page.parent = None
            page.status = form.cleaned_data['status']
            page.slug = form.cleaned_data['slug']
            page.template = form.cleaned_data.get('template', None)
            page.save()
            #change_message.append(_('Changed %s.') % get_text_list(manipulator.fields_changed, _('and')))
            #LogEntry.objects.log_action(request.user.id, ContentType.objects.get_for_model(model).id, pk_value, force_unicode(new_object), CHANGE, change_message)
            msg = _('The %(name)s "%(obj)s" was changed successfully.') % {'name': force_unicode(opts.verbose_name), 'obj': force_unicode(page)}
            request.user.message_set.create(message=msg)
            return HttpResponseRedirect("../")
    else:
        l=Language.get_from_request(request)
        if page.parent:
            parent_id  = page.parent.id
        else:
            parent_id = None
        form = get_form(request, {'title':Content.get_content(page, l, 0), 'body':Content.get_content(page, l, 1), 'status':page.status, 'slug':page.slug, 'template':page.template, 'parent':parent_id}, page)

    return 'admin/pages/page/change_form.html', locals()

@staff_member_required
@auto_render
def list_page(request):
    opts = Page._meta
    pages = Page.objects.filter(parent__isnull=True)
    return 'admin/pages/page/change_list.html', locals()
