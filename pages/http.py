"""Page CMS functions related to the ``request`` object."""
from django.core.handlers.base import BaseHandler
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import loader, Context, RequestContext
from django.core.urlresolvers import reverse
from pages import settings

def get_request_mock():
    """Build a ``request`` mock that can be used for testing."""
    bh = BaseHandler()
    bh.load_middleware()
    request = WSGIRequest({
        'REQUEST_METHOD': 'GET',
        'SERVER_NAME': 'test',
        'SERVER_PORT': '8000',
        'HTTP_HOST': 'testhost',
    })
    # Apply request middleware
    for middleware_method in bh._request_middleware:
        # LocaleMiddleware should never be applied a second time because
        # it would broke the current real request language
        if 'LocaleMiddleware' not in str(middleware_method.im_class):
            response = middleware_method(request)
    return request

class AutoRenderHttpError(Exception):
    """Cannot return context dictionary because a view returned an
    ``HttpResponse`` when a (template_name, context) tuple was expected."""
    pass

def auto_render(func):
    """
    This view decorator automatically calls the ``render_to_response``
    shortcut. A view that use this decorator should return a tuple of this
    form : (template name, context) instead of a ``HttpRequest`` object.
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

def get_slug_and_relative_path(path, lang=None):
    """Return the page's slug and relative path."""
    root = reverse('pages-root')
    if path.startswith(root):
        path = path[len(root):]
    if len(path) and path[-1] == '/':
        path = path[:-1]
    slug = path.split("/")[-1]
    if settings.PAGE_USE_LANGUAGE_PREFIX:
        lang = path.split("/")[0]
        path = path[(len(lang) + 1):]
    return slug, path, lang

def get_template_from_request(request, page=None):
    """
    Gets a valid template from different sources or falls back to the
    default template.
    """
    if settings.PAGE_TEMPLATES is None:
        return settings.DEFAULT_PAGE_TEMPLATE
    template = request.REQUEST.get('template', None)
    if template is not None and \
            (template in dict(settings.PAGE_TEMPLATES).keys() or
            template == settings.DEFAULT_PAGE_TEMPLATE):
        return template
    if page is not None:
        return page.get_template()
    return settings.DEFAULT_PAGE_TEMPLATE

def get_language_from_request(request):
    """Return the most obvious language according the request."""
    language = request.GET.get('language', None)
    if language:
        return language

    if hasattr(request, 'LANGUAGE_CODE'):
        return settings.PAGE_LANGUAGE_MAPPING(str(request.LANGUAGE_CODE))
    else:
        return settings.PAGE_DEFAULT_LANGUAGE

