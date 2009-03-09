# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.db.models import signals
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.sites.models import Site, RequestSite, SITE_CACHE
from pages import settings
from pages.models import Content, Page

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
    
    client_language = settings.PAGE_LANGUAGE_MAPPING(str(request.LANGUAGE_CODE))

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

from django.core.urlresolvers import reverse
def get_page_from_slug(slug, request):
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
