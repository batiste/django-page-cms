from pages.utils import auto_render
from pages.models import Language, Content, Page, has_page_permission, has_page_add_permission, get_page_valid_targets_queryset
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django import forms
from django.db import models
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.utils.encoding import force_unicode, smart_str
from django.utils.translation import ugettext as _
from django.template import loader, Context, RequestContext, TemplateDoesNotExist
from django.template.loader_tags import ExtendsNode
# must be imported like this for isinstance
from django.templatetags.pages import PlaceholderNode
import settings
from mptt.exceptions import InvalidMove
from mptt.forms import MoveNodeForm

def get_placeholders(request, template_name):
    """Return a list of PlaceholderNode found in the given template"""
    try:
        temp = loader.get_template(template_name)
    except TemplateDoesNotExist:
        return []
    from pages.views import details
    context = details(request, only_context=True)
    temp.render(RequestContext(request, context))
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

    language_choices = settings.PAGE_LANGUAGES
    l = Language.get_from_request(request, current_page)
    if hasattr(settings, 'PAGE_TEMPLATES') and settings.PAGE_TEMPLATES:
        template_choices = list(settings.PAGE_TEMPLATES)
        template_choices.insert(0,('',_('Inherit')))
    else:
        template_choices = False
    
    class PageForm(forms.Form):
        slug = forms.CharField(widget=forms.TextInput(), required=True)
        title = forms.CharField(widget=forms.TextInput(), required=request.POST)
        language = forms.ChoiceField(choices=language_choices, initial=l)
        status = forms.ChoiceField(widget=forms.RadioSelect({'class':'radiolist'}), choices=Page.STATUSES)
        
        if settings.PAGE_TAGGING:
            from tagging.forms import TagField
            tags = TagField(required=False)
            
        if template_choices:
            template = forms.ChoiceField(choices=template_choices, required=False)
        
        def clean_slug(self):
            from django.template.defaultfilters import slugify
            slug = slugify(self.cleaned_data['slug'])
            """if settings.PAGE_UNIQUE_SLUG_REQUIRED:
                if current_page and Page.objects.exclude(pk=current_page.id).filter(slug=slug):
                    raise forms.ValidationError('Another page with this slug already exists')
                if current_page is None and Page.objects.filter(slug=slug):
                    raise forms.ValidationError('Another page with this slug already exists')"""
            return slug
        
    from django.http import QueryDict
    
    if dict and type(dict) is not QueryDict:
        dict['language'] = l
        
    template = settings.DEFAULT_PAGE_TEMPLATE if current_page is None else current_page.get_template()
    for placeholder in get_placeholders(request, template):
        if placeholder.widget == 'TextInput':
            w = forms.TextInput()
        elif placeholder.widget == 'RichTextarea':
            w = forms.Textarea({'class':'rte'})
        else:
            w = forms.Textarea()
        if placeholder.name not in ['title', 'slug']:
            PageForm.base_fields[placeholder.name] = forms.CharField(widget=w, required=False)
        
    if dict:
        p = PageForm(dict)
    else:
        p = PageForm()
    
    return p

# these mandatory fields are not versioned
mandatory_page_fields = ['title', 'slug']

@staff_member_required
@auto_render
def add(request):
    """create a new page for a particular language"""
    if not has_page_add_permission(request):
        raise Http404
    opts = Page._meta
    app_label = _('Pages')
    add = True
    from settings import MEDIA_URL
    placeholders = get_placeholders(request, settings.DEFAULT_PAGE_TEMPLATE)
    if(request.POST):
        form = get_form(request, request.POST)
        if form.is_valid():
            status = form.cleaned_data['status']
            #slug = form.cleaned_data['slug']
            template = form.cleaned_data.get('template', None)
            page = Page(author=request.user, status=status, template=template)
            page.save()
            if settings.PAGE_TAGGING:
                page.tags = form.cleaned_data['tags']
            
            language = form.cleaned_data['language']
            
            if "target" in request.GET:
                target = Page.objects.get(pk=int(request.GET["target"]))
                page.move_to(target, request.GET["position"])
            
            for m in mandatory_page_fields:
                Content.set_or_create_content(page, language, m, form.cleaned_data[m])
            
            for placeholder in get_placeholders(request, page.get_template()):
                if placeholder.name in form.cleaned_data:
                    Content.set_or_create_content(page, language, placeholder.name, form.cleaned_data[placeholder.name])
            #Content.set_or_create_content(page, language, 'slug', form.cleaned_data['slug'])
            
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
    placeholders = get_placeholders(request, page.get_template())
    original = page
    language = Language.get_from_request(request)
    
    if request.POST:
        
        form = get_form(request, request.POST, page)
        
        if form.is_valid():
            language = form.cleaned_data['language']
            page.status = form.cleaned_data['status']
            page.template = form.cleaned_data.get('template', None)
            page.save()
            if settings.PAGE_TAGGING:
                page.tags = form.cleaned_data['tags']
            
            mandatory = ['title', 'slug']
            for m in mandatory_page_fields:
                Content.set_or_create_content(page, language, m, form.cleaned_data[m])
                
            for placeholder in get_placeholders(request, page.get_template()):
                if placeholder.name in form.cleaned_data and placeholder.name not in mandatory:
                    # we need create a new content if revision is enabled
                    if settings.PAGE_CONTENT_REVISION and placeholder.name \
                            not in settings.PAGE_CONTENT_REVISION_EXCLUDE_LIST:
                        Content.create_content_if_changed(page, language, placeholder.name, form.cleaned_data[placeholder.name])
                    else:
                        Content.set_or_create_content(page, language, placeholder.name, form.cleaned_data[placeholder.name])
            
            msg = _('The %(name)s "%(obj)s" was changed successfully.') % {'name': force_unicode(opts.verbose_name), 'obj': force_unicode(page)}
            request.user.message_set.create(message=msg)
            return HttpResponseRedirect("../")
    else:
        traduction_language = settings.PAGE_LANGUAGES
        if settings.PAGE_TAGGING:
            tag_list = ", ".join([str(t) for t in page.tags])
        else:
            tag_list = None
        dict = {'status':page.status, 'template':page.template, 'tags':tag_list, 'slug':page.slug(language=language)}
        for placeholder in placeholders:
            dict[placeholder.name] = Content.get_content(page, language, placeholder.name)
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
    """Move the page to the requested target, at the given position"""
    page = Page.objects.get(pk=int(page_id))
    target = Page.objects.get(pk=int(request.POST['target']))
    page.move_to(target, request.POST['position'])
    return list_pages(request, template_name="pages/change_list_table.html")

@staff_member_required
def change_status(request, page_id):
    """Switch the status of a page"""
    if request.POST:
        page = Page.objects.get(pk=int(page_id))
        if page.status == 0:
            page.status = 1
            page.save()
        elif page.status == 1:
            page.status = 0
            page.save()
        return HttpResponse(page.status)
    else:
        raise Http404

@staff_member_required
@auto_render
def traduction(request, page_id, language_id):
    page = Page.objects.get(pk=page_id)
    context = {}
    lang = language_id
    placeholders = get_placeholders(page.get_template())
    print Content.get_content(page, language_id, "title")
    if Content.get_content(page, language_id, "title") is None:
        language_error = True
    return 'pages/traduction_helper.html', locals()
    
@staff_member_required
@auto_render
def content(request, page_id, content_id):
    c = Content.objects.get(pk=content_id)
    return HttpResponse(c.body)

@staff_member_required
def modify_content(request, page_id, content_id, language_id):
    if request.POST:
        content = request.POST.get('content', False)
        if not content:
            raise Http404
        page = Page.objects.get(pk=page_id)
        if not has_page_permission(request, page):
            raise Http404
        if settings.PAGE_CONTENT_REVISION:
            Content.create_content_if_changed(page, language_id, content_id, content)
        else:
            Content.set_or_create_content(page, language_id, content_id, content)

        return HttpResponse("oki")
    raise Http404