"""Page CMS functions related to the ``request`` object."""
from pages import settings


LANGUAGE_KEYS = [key for (key, value) in settings.PAGE_LANGUAGES]


def get_request_mock():
    """Build a ``request`` mock up for tests"""
    from django.test.client import RequestFactory
    from django.core.handlers.base import BaseHandler
    factory = RequestFactory()

    request = factory.get('/')
    
    class FakeUser():
        is_authenticated = False
        is_staff = False

    request.user = FakeUser()
    request.session = {}

    return request


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
