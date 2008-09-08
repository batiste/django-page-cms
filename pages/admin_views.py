from pages.utils import auto_render
from pages.models import Language, Content, Page, has_page_permission, has_page_add_permission, get_page_valid_targets_queryset
#from hierarchical.models import HierarchicalNode, HierarchicalObject
from django.contrib.admin.views.decorators import staff_member_required
from django import forms
from django.db import models
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.utils.encoding import force_unicode, smart_str
from django.utils.translation import ugettext as _
from django.template import loader, Context, TemplateDoesNotExist
from django.template.loader_tags import ExtendsNode
# must be imported like this for isinstance
from django.templatetags.pages import PlaceholderNode
import settings
from mptt.exceptions import InvalidMove
from mptt.forms import MoveNodeForm

def get_placeholders(template_name):
    """Return a list of PlaceholderNode found in the given template"""
    try:
        temp = loader.get_template(template_name)
    except TemplateDoesNotExist:
        return []
    temp.render(Context())
    list = []
    placeholders_recursif(temp.nodelist, list)
    return list
        
def placeholders_recursif(nodelist, list):    
    """Recursively search into a template node list for PlaceholderNode node"""
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
    """Dynamicaly create a form to create/modify a page in the admin interface"""

    language_choices = [(lang.id, lang.name) for lang in Language.objects.all()]
    l = Language.get_from_request(request, current_page)
    import settings
    if hasattr(settings, 'PAGE_TEMPLATES'):
        template_choices = list(settings.PAGE_TEMPLATES)
        template_choices.insert(0,('',_('Inherit')))
    else:
        template_choices = False
    
    class PageForm(forms.Form):
        slug = forms.CharField(widget=forms.TextInput(), required=True)
        title = forms.CharField(widget=forms.TextInput(), required=request.POST)
        language = forms.ChoiceField(choices=language_choices, initial=l.id)
        status = forms.ChoiceField(choices=Page.STATUSES)
        if template_choices:
            template = forms.ChoiceField(choices=template_choices, required=False)
        
        def clean_slug(self):
            from django.template.defaultfilters import slugify
            slug = slugify(self.cleaned_data['slug'])
            if current_page and Page.objects.exclude(pk=current_page.id).filter(slug=slug):
                raise forms.ValidationError('Another page with this slug already exists')
            if current_page is None and Page.objects.filter(slug=slug):
                raise forms.ValidationError('Another page with this slug already exists')
            return slug
        
    from django.http import QueryDict
    
    if dict and type(dict) is not QueryDict:
        dict['language'] = l.id
        
    template = settings.DEFAULT_PAGE_TEMPLATE if current_page is None else current_page.get_template()
    for placeholder in get_placeholders(template):
        if placeholder.widget == 'TextInput':
            w = forms.TextInput()
        elif placeholder.widget == 'RichTextarea':
            w = forms.Textarea({'class':'rte'})
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
    if not has_page_add_permission(request):
        raise Http404
    opts = Page._meta
    app_label = _('Pages')
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
            language = Language.objects.get(pk=form.cleaned_data['language'])
            
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
    app_label = _('Pages')
    change = True
    has_absolute_url = True
    from settings import MEDIA_URL
    page = Page.objects.get(pk=page_id)
    if not has_page_permission(request, page):
        raise Http404
    placeholders = get_placeholders(page.get_template())
    original = page
    page_queryset = get_page_valid_targets_queryset(request, page)
    
    if(request.POST):
        if page_queryset is not None:
            move_form = MoveNodeForm(page, request.POST, valid_targets=page_queryset)
        else:
            move_form = MoveNodeForm(page, request.POST)
            
        form = get_form(request, request.POST, page)
        if form.is_valid():
            language = Language.objects.get(pk=form.cleaned_data['language'])
            page.status = form.cleaned_data['status']
            page.slug = form.cleaned_data['slug']
            page.template = form.cleaned_data.get('template', None)
            page.save()
            for placeholder in get_placeholders(page.get_template()):
                if placeholder.name in form.cleaned_data:
                    Content.set_or_create_content(page, language, placeholder.name, form.cleaned_data[placeholder.name])
            
            if move_form.is_valid():
                move_form.save()
            msg = _('The %(name)s "%(obj)s" was changed successfully.') % {'name': force_unicode(opts.verbose_name), 'obj': force_unicode(page)}
            request.user.message_set.create(message=msg)
            return HttpResponseRedirect("../")
    else:
        if page_queryset is not None:
            move_form = MoveNodeForm(page, valid_targets=page_queryset)
        else:
            move_form = MoveNodeForm(page)
        l=Language.get_from_request(request)
        traduction_language = Language.objects.exclude(pk=l.id)
        dict = {'status':page.status, 'slug':page.slug, 'template':page.template}
        for placeholder in placeholders:
            dict[placeholder.name] = Content.get_content(page, l, placeholder.name)
        form = get_form(request, dict, page)

    return 'pages/change_form.html', locals()

@staff_member_required
@auto_render
def list_pages(request):
    """List root pages"""
    name = _("page")
    app_label = _('Pages')
    from settings import MEDIA_URL
    opts = Page._meta
    has_add_permission = has_page_add_permission(request)
    pages = Page.objects.filter(parent__isnull=True).order_by("tree_id")
    return 'pages/change_list.html', locals()

@staff_member_required
def valid_targets_list(request, page_id):
    """A list of valid targets to move a page"""
    page = Page.objects.get(pk=page_id)
    query = get_page_valid_targets_queryset(request, page)
    return HttpResponse(",".join([str(p.id) for p in query]))

@staff_member_required
def move_page(request, page_id):
    page = Page.objects.get(pk=int(page_id))
    target = Page.objects.get(pk=int(request.POST['target']))
    page.move_to(target, request.POST['position'])
    return list_pages(request, template_name="pages/change_list_table.html")

@staff_member_required
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
