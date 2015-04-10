"""Page CMS functions related to the ``request`` object."""
from pages import settings
from django.template import RequestContext
try:
    from io import StringIO
except ImportError:
    from io import StringIO

LANGUAGE_KEYS = [key for (key, value) in settings.PAGE_LANGUAGES]

def get_request_mock():
    """Build a ``request`` mock up that is used in to render
    the templates in the most fidel environement as possible.

    This fonction is used in the get_placeholders method to
    render the input template and search for the placeholder
    within.
    """
    from django.test.client import RequestFactory
    from django.core.handlers.base import BaseHandler
    factory = RequestFactory()
    basehandler = BaseHandler()
    basehandler.load_middleware()
    
    request = factory.get('/')
    # Apply request middleware
    for middleware_method in basehandler._request_middleware:
        # LocaleMiddleware should never be applied a second time because
        # it would broke the current real request language
        if 'LocaleMiddleware' not in str(middleware_method.__self__.__class__):
            response = middleware_method(request)
    
    return request


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
            extra_context_var = kwargs.pop('extra_context_var', None)
            if extra_context_var:
                kwargs.update({extra_context_var: context})
            else:
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
    template = request.POST.get('template', request.GET.get('template', None))
    if template is not None and \
            (template in list(dict(page_templates).keys()) or
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
