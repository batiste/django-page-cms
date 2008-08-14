from hierarchical.utils import auto_render
from pages.models import Language, Content, Page
from hierarchical.models import HierarchicalNode, HierarchicalObject
from django.contrib.admin.views.decorators import staff_member_required
from django import forms
from django.db import models
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.encoding import force_unicode, smart_str
from django.utils.translation import ugettext as _
from django.template import loader, Context, TemplateDoesNotExist
from django.template.loader_tags import ExtendsNode
# must be imported like this for isinstance
from django.templatetags.pages import PlaceholderNode
import settings

def get_placeholders(template_name):
    try:
        temp = loader.get_template(template_name)
    except TemplateDoesNotExist:
        return []
    temp.render(Context())
    list = []
    placeholders_recursif(temp.nodelist, list)
    return list
        
def placeholders_recursif(nodelist, list):
    for node in nodelist:
        if isinstance(node, PlaceholderNode):
            list.append(node)
            node.render(Context())
        for key in ('nodelist', 'nodelist_true', 'nodelist_false'):
            if hasattr(node, key):
                try:
                    placeholders_recursif(getattr(node, key), list)
                except:
                    pass
    for node in nodelist:
        if isinstance(node, ExtendsNode):
            placeholders_recursif(node.get_parent(Context()).nodelist, list)

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
    
    template = settings.DEFAULT_PAGE_TEMPLATE if current_page is None else current_page.get_template()
    for placeholder in get_placeholders(template):
        if placeholder.widget == 'TextInput':
            w = forms.TextInput()
        else:
            w = forms.Textarea()
        if placeholder.name != "title":
            PageForm.base_fields[placeholder.name] = forms.CharField(widget=w, required=False)
        
    if dict:
        p = PageForm(dict)
    else:
        p = PageForm()
    
    return p
    
@staff_member_required
@auto_render
def add(request):
    """create a new page for a particular language"""
    opts = Page._meta
    add = True
    placeholders = get_placeholders(settings.DEFAULT_PAGE_TEMPLATE)
    if(request.POST):
        form = get_form(request, request.POST)
        if form.is_valid():
            status = form.cleaned_data['status']
            slug = form.cleaned_data['slug']
            template = form.cleaned_data.get('template', None)
            page = Page(author=request.user, status=status, slug=slug, template=template)
            page.save()
            HierarchicalObject.update_for_object(page, form.cleaned_data['node'])
            language=Language.objects.get(pk=form.cleaned_data['language'])
            
            for placeholder in get_placeholders(page.get_template()):
                if placeholder.name in form.cleaned_data:
                    Content.set_or_create_content(page, language, placeholder.name, form.cleaned_data[placeholder.name])
            
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
    placeholders = get_placeholders(page.get_template())
    original = page
    if(request.POST):
        form = get_form(request, request.POST, page)
        if form.is_valid():
            language=Language.objects.get(pk=form.cleaned_data['language'])
            page.status = form.cleaned_data['status']
            page.slug = form.cleaned_data['slug']
            page.template = form.cleaned_data.get('template', None)
            page.save()
            for placeholder in get_placeholders(page.get_template()):
                if placeholder.name in form.cleaned_data:
                    Content.set_or_create_content(page, language, placeholder.name, form.cleaned_data[placeholder.name])
            
            HierarchicalObject.update_for_object(page, form.cleaned_data['node'])
            msg = _('The %(name)s "%(obj)s" was changed successfully.') % {'name': force_unicode(opts.verbose_name), 'obj': force_unicode(page)}
            request.user.message_set.create(message=msg)
            return HttpResponseRedirect("../")
    else:
        l=Language.get_from_request(request)
        traduction_language = Language.objects.exclude(pk=l.id)
        dict = {'status':page.status, 'slug':page.slug, 'template':page.template}
        for placeholder in placeholders:
            dict[placeholder.name] = Content.get_content(page, l, placeholder.name)
        form = get_form(request, dict, page)

    return 'pages/change_form.html', locals()

#@staff_member_required
@auto_render
def traduction(request, page_id, language_id):
    page = Page.objects.get(pk=page_id)
    l = Language.objects.get(pk=language_id)
    context = {}
    for placeholder in get_placeholders(page.get_template()):
        context[placeholder.name] = Content.get_content(page, l, placeholder.name, True)
    if Content.get_content(page, l, "title") !=  context['title']:
        context['language_error'] = True
    return 'pages/traduction_helper.html', context
