# -*- coding: utf-8 -*-
from django.template import loader, Context, RequestContext, TemplateDoesNotExist
from django.template.loader_tags import ExtendsNode
from django.http import Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.db.models import signals
from django.http import HttpResponse, HttpResponseRedirect
from django.core.handlers.wsgi import WSGIRequest
from django.contrib.sites.models import Site, RequestSite, SITE_CACHE
from pages import settings

def get_placeholders(template_name):
    """
    Return a list of PlaceholderNode found in the given template
    """
    try:
        temp = loader.get_template(template_name)
    except TemplateDoesNotExist:
        return []
    
    request = WSGIRequest({'REQUEST_METHOD': 'GET'})
    request.session = {}
    
    try:
        # to avoid circular import
        from pages.views import details
        context = details(request, only_context=True)
    except Http404:
        context = {}
    temp.render(RequestContext(request, context))
    plist = []
    placeholders_recursif(temp.nodelist, plist)
    return plist

def placeholders_recursif(nodelist, plist):
    """
    Recursively search into a template node list for PlaceholderNode node
    """
    # to avoid circular import
    # must be imported like this for isinstance
    from django.templatetags.pages_tags import PlaceholderNode
    for node in nodelist:
        if isinstance(node, PlaceholderNode):
            already_in_plist = False
            for p in plist:
                if p.name == node.name:
                    already_in_plist = True
            if not already_in_plist:
                plist.append(node)
            node.render(Context())
        for key in ('nodelist', 'nodelist_true', 'nodelist_false'):
            if hasattr(node, key):
                try:
                    placeholders_recursif(getattr(node, key), plist)
                except:
                    pass
    for node in nodelist:
        if isinstance(node, ExtendsNode):
            placeholders_recursif(node.get_parent(Context()).nodelist, plist)

def auto_render(func):
    """Decorator that put automaticaly the template path in the context dictionary
    and call the render_to_response shortcut"""
    def _dec(request, *args, **kwargs):
        t = None
        if kwargs.get('only_context', False):
            # return only context dictionary
            del(kwargs['only_context'])
            response = func(request, *args, **kwargs)
            if isinstance(response, HttpResponse) or isinstance(response, HttpResponseRedirect):
                raise Except("cannot return context dictionary because a HttpResponseRedirect as been found")
            (template_name, context) = response
            return context
        if "template_name" in kwargs:
            t = kwargs['template_name']
            del kwargs['template_name']
        response = func(request, *args, **kwargs)
        if isinstance(response, HttpResponse) or isinstance(response, HttpResponseRedirect):
            return response
        (template_name, context) = response
        if not t:
            t = template_name
        context['template_name'] = t
        return render_to_response(t, context, context_instance=RequestContext(request))
    return _dec

def get_template_from_request(request, obj=None):
    """
    Gets a valid template from different sources or falls back to the default
    template.
    """
    if settings.PAGE_TEMPLATES is None:
        return settings.DEFAULT_PAGE_TEMPLATE
    template = request.REQUEST.get('template', None)
    if template is not None and \
            template in dict(settings.PAGE_TEMPLATES).keys():
        return template
    if obj is not None:
        return obj.get_template()
    return settings.DEFAULT_PAGE_TEMPLATE

def get_language_from_request(request, current_page=None):
    """
    Return the most obvious language according the request
    """
    # first try the GET parameter
    language = request.GET.get('language', None)
    if language:
        return language

    if hasattr(request, 'LANGUAGE_CODE'):
        client_language = settings.PAGE_LANGUAGE_MAPPING(str(request.LANGUAGE_CODE))
    else:
        client_language = settings.PAGE_DEFAULT_LANGUAGE
        
    # then try to get the right one for the page
    if current_page:
        # try to get the language that match the client language
        languages = current_page.get_languages()
        for lang in languages:
            if client_language == str(lang):
                return client_language

    # last resort
    return settings.PAGE_DEFAULT_LANGUAGE

def has_page_add_permission(request, page=None):
    """
    Return true if the current user has permission to add a new page.
    """
    if not settings.PAGE_PERMISSION:
        return True
    else:
        from pages.models import PagePermission
        permission = PagePermission.objects.get_page_id_list(request.user)
        if permission == "All":
            return True
    return False

# TODO: move this in the manager
def get_page_from_slug(slug, request, lang=None):
    from pages.models import Content, Page
    from django.core.urlresolvers import reverse
    lang = get_language_from_request(request)
    relative_url = request.path.replace(reverse('pages-root'), '')
    page_ids = Content.objects.get_page_ids_by_slug(slug)
    pages_list = Page.objects.filter(id__in=page_ids)
    current_page = None
    if len(pages_list) == 1:
        return pages_list[0]
    if len(pages_list) > 1:
        for page in pages_list:
            if page.get_url(lang) == relative_url:
                return page
    return None
