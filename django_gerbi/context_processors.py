"""Context processors for Page CMS."""
from django_gerbi import settings
from django_gerbi.models import Page


def media(request):
    """Adds media-related variables to the `context`."""
    return {
        'DJANGO_GERBI_MEDIA_URL': settings.DJANGO_GERBI_MEDIA_URL,
        'DJANGO_GERBI_USE_SITE_ID': settings.DJANGO_GERBI_USE_SITE_ID,
        'DJANGO_GERBI_HIDE_SITES': settings.DJANGO_GERBI_HIDE_SITES,
        'DJANGO_GERBI_LANGUAGES': settings.DJANGO_GERBI_LANGUAGES,
    }


def pages_navigation(request):
    """Adds essential django_gerbi variables to the `context`."""
    page_set = Page.objects.navigation().order_by("tree_id")
    return {
        'pages_navigation': page_set,
        'current_page': None
    }
