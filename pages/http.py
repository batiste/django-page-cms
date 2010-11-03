"""Page CMS functions related to the ``request`` object."""
from django.core.handlers.base import BaseHandler
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from pages import settings

LANGUAGE_KEYS = [key for (key, value) in settings.PAGE_LANGUAGES]


def get_request_mock():
    """Build a ``request`` mock up that can be used for testing."""
    basehandler = BaseHandler()
    basehandler.load_middleware()
    request = WSGIRequest({
        'REQUEST_METHOD': 'GET',
        'SERVER_NAME': 'test',
        'SERVER_PORT': '8000',
        'HTTP_HOST': 'testhost',
    })
    # Apply request middleware
    for middleware_method in basehandler._request_middleware:
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
    def auto_render_decorator(request, *args, **kwargs):
        template_override = kwargs.pop('template_name', None)
        only_context = kwargs.pop('only_context', False)
        only_response = kwargs.pop('only_response', False)
        if only_context or only_response:
            # return only context dictionary or response
            response = func(request, *args, **kwargs)
            if only_response:
                return response
            if isinstance(response, HttpResponse):
                raise AutoRenderHttpError(AutoRenderHttpError.__doc__)
            (template_name, context) = response
            return context
        response = func(request, *args, **kwargs)
        if isinstance(response, HttpResponse):
            return response
        (template_name, context) = response
        template_name = context['template_name'] = (template_override or
            template_name)
        return render_to_response(template_name, context,
                            context_instance=RequestContext(request))
    return auto_render_decorator


def pages_view(view):
    """
    Make sure the decorated view gets the essential pages
    variables.
    """
    def pages_view_decorator(request, *args, **kwargs):
        # if the current page is already there
        if(kwargs.get('current_page', False) or
            kwargs.get('pages_navigation', False)):
            return view(request, *args, **kwargs)

        path = kwargs.pop('path', None)
        lang = kwargs.pop('lang', None)
        if path:
            from pages.views import details
            response = details(request, path=path, lang=lang,
                only_context=True, delegation=False)
            context = response
            kwargs.update(context)
        return view(request, *args, **kwargs)
    return pages_view_decorator


def get_slug(path):
    """
    Return the page's slug

        >>> get_slug('/test/function/')
        function
    """
    if path.endswith('/'):
        path = path[:-1]
    return path.split("/")[-1]


def remove_slug(path):
    """
    Return the remainin part of the path

        >>> remove_slug('/test/some/function/')
        test/some
    """
    if path.endswith('/'):
        path = path[:-1]
    if path.startswith('/'):
        path = path[1:]
    if "/" not in path or not path:
        return None
    parts = path.split("/")[:-1]
    return "/".join(parts)


def get_template_from_request(request, page=None):
    """
    Gets a valid template from different sources or falls back to the
    default template.
    """
    page_templates = settings.get_page_templates()
    if len(page_templates) == 0:
        return settings.PAGE_DEFAULT_TEMPLATE
    template = request.REQUEST.get('template', None)
    if template is not None and \
            (template in dict(page_templates).keys() or
            template == settings.PAGE_DEFAULT_TEMPLATE):
        return template
    if page is not None:
        return page.get_template()
    return settings.PAGE_DEFAULT_TEMPLATE


def get_language_from_request(request):
    """Return the most obvious language according the request."""
    language = request.GET.get('language', None)
    if language:
        return language

    if hasattr(request, 'LANGUAGE_CODE'):
        lang = settings.PAGE_LANGUAGE_MAPPING(str(request.LANGUAGE_CODE))
        if lang not in LANGUAGE_KEYS:
            return settings.PAGE_DEFAULT_LANGUAGE
        else:
            return lang
    else:
        return settings.PAGE_DEFAULT_LANGUAGE
