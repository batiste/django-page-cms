from utils import auto_render
from pages.models import Language, Content, Page
from hierarchical.models import HierarchicalNode, HierarchicalObject
from django.contrib.admin.views.decorators import staff_member_required
from django import newforms as forms
from django.db import models
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.encoding import force_unicode, smart_str
from django.utils.translation import ugettext as _

def get_form(request, dict=None, current_page=None):
    """get the custom form to create or edit a page in the admin interface"""

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
        node = forms.ModelChoiceField(HierarchicalNode.objects.all(), required=False)
        if template_choices:
            template = forms.ChoiceField(choices=template_choices, required=False)
        
        def clean_slug(self):
            from django.template.defaultfilters import slugify
            if current_page and Page.objects.exclude(pk=current_page.id).filter(slug=slugify(self.cleaned_data['slug'])):
                    raise forms.ValidationError('Another page with this slug already exists')
            return slugify(self.cleaned_data['slug'])
        
    from django.http import QueryDict
    
    if dict and type(dict) is not QueryDict:
        dict['language'] = l.id
        node = HierarchicalNode.get_nodes_by_object(current_page)
        if node:
            dict['node'] = node[0].id
        
    if dict:
        return PageForm(dict)
    
    return PageForm()
    
@staff_member_required
@auto_render
def add(request):
    """create a new page for a particular language"""
    opts = Page._meta
    add = True
    if(request.POST):
        form = get_form(request, request.POST)
        if form.is_valid():
            status = form.cleaned_data['status']
            slug = form.cleaned_data['slug']
            template = form.cleaned_data.get('template', None)
            page = Page(author=request.user, status=status, slug=slug, template=template)
            page.save()
            #if form.cleaned_data['node']:
            HierarchicalObject.update_for_object(page, form.cleaned_data['node'])
            language=Language.objects.get(pk=form.cleaned_data['language'])
            Content.set_or_create_content(page, language, 0, form.cleaned_data['title'])
            Content.set_or_create_content(page, language, 1, form.cleaned_data['body'])
            msg = _('The %(name)s "%(obj)s" was added successfully.') % {'name': force_unicode(opts.verbose_name), 'obj': force_unicode(page)}
            request.user.message_set.create(message=msg)
            return HttpResponseRedirect("../")
    else:
        form = get_form(request)

    return 'pages/change_form.html', locals()

@staff_member_required
@auto_render
def modify(request, page_id):
    """modifiy a page in a particular language"""
    opts = Page._meta
    change = True
    has_absolute_url = True
    page = Page.objects.get(pk=page_id)
    original = page
    #content_type_id = 
    #object_id = page.id
    if(request.POST):
        form = get_form(request, request.POST, page)
        if form.is_valid():
            language=Language.objects.get(pk=form.cleaned_data['language'])
            Content.set_or_create_content(page, language, 0, form.cleaned_data['title'])
            Content.set_or_create_content(page, language, 1, form.cleaned_data['body'])
            page.status = form.cleaned_data['status']
            page.slug = form.cleaned_data['slug']
            page.template = form.cleaned_data.get('template', None)
            page.save()
            HierarchicalObject.update_for_object(page, form.cleaned_data['node'])
            msg = _('The %(name)s "%(obj)s" was changed successfully.') % {'name': force_unicode(opts.verbose_name), 'obj': force_unicode(page)}
            request.user.message_set.create(message=msg)
            return HttpResponseRedirect("../")
    else:
        l=Language.get_from_request(request)
        traduction_language = Language.objects.exclude(pk=l.id)
        form = get_form(request, {'title':Content.get_content(page, l, 0), 'body':Content.get_content(page, l, 1), 'status':page.status, 'slug':page.slug, 'template':page.template}, page)

    return 'pages/change_form.html', locals()

#@staff_member_required
@auto_render
def traduction(request, page_id, language_id):
    page = Page.objects.get(pk=page_id)
    l = Language.objects.get(pk=language_id)
    title = Content.get_content(page, l, 0, True)
    if Content.get_content(page, l, 0) !=  title:
        language_error = True
    body = Content.get_content(page, l, 1, True)
    return 'pages/traduction_helper.html', locals()
