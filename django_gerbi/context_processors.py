"""Context processors for Page CMS."""
from django_gerbi import settings
from django_gerbi.models import Page


def media(request):
    """Adds media-related variables to the `context`."""
    return {
        'GERBI_MEDIA_URL': settings.GERBI_MEDIA_URL,
        'GERBI_USE_SITE_ID': settings.GERBI_USE_SITE_ID,
        'GERBI_HIDE_SITES': settings.GERBI_HIDE_SITES,
        'GERBI_LANGUAGES': settings.GERBI_LANGUAGES,
    }


def pages_navigation(request):
    """Adds essential django_gerbi variables to the `context`."""
    page_set = Page.objects.navigation().order_by("tree_id")
    return {
        'pages_navigation': page_set,
        'current_page': None
    }
