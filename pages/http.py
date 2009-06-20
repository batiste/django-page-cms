"""Page CMS functions related to the request object"""
from django.core.handlers.base import BaseHandler
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import loader, Context, RequestContext
from pages import settings

def get_request_mock():
    """Build a request mock that can be used for testing."""
    bh = BaseHandler()
    bh.load_middleware()
    request = WSGIRequest({
        'REQUEST_METHOD': 'GET',
        'SERVER_NAME': 'test',
        'SERVER_PORT': '8000',
    })
    # Apply request middleware
    for middleware_method in bh._request_middleware:
        # LocaleMiddleware should never be applied a second time because
        # it would broke the current real request language
        if 'LocaleMiddleware' not in str(middleware_method.im_class):
            response = middleware_method(request)
    return request

class AutoRenderHttpError(Exception):
    """cannot return context dictionary because a view returned an HTTP
    response when a (template_name, context) tuple was expected"""
    pass

def auto_render(func):
    """A decorator which automatically inserts the template path into the
    context and calls the render_to_response shortcut
    """
    def _dec(request, *args, **kwargs):
        template_override = kwargs.pop('template_name', None)
        only_context = kwargs.pop('only_context', False)
        if only_context:
            # return only context dictionary
            response = func(request, *args, **kwargs)
            if isinstance(response, HttpResponse):
                raise AutoRenderHttpError
            (template_name, context) = response
            return context
        response = func(request, *args, **kwargs)
        if isinstance(response, HttpResponse):
            return response
        (template_name, context) = response
        t = context['template_name'] = template_override or template_name
        return render_to_response(t, context,
context_instance=RequestContext(request))
    return _dec


def get_template_from_request(request, obj=None):
    """Gets a valid template from different sources or falls back to the
    default template.
    """
    if settings.PAGE_TEMPLATES is None:
        return settings.DEFAULT_PAGE_TEMPLATE
    template = request.REQUEST.get('template', None)
    if template is not None and \
            (template in dict(settings.PAGE_TEMPLATES).keys() or
            template == settings.DEFAULT_PAGE_TEMPLATE):
        return template
    if obj is not None:
        return obj.get_template()
    return settings.DEFAULT_PAGE_TEMPLATE

def get_language_from_request(request, current_page=None):
    """Return the most obvious language according the request."""
    # first try the GET parameter
    language = request.GET.get('language', None)
    if language:
        return language

    if hasattr(request, 'LANGUAGE_CODE'):
        client_language = \
            settings.PAGE_LANGUAGE_MAPPING(str(request.LANGUAGE_CODE))
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