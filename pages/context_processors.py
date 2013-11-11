"""Context processors for Page CMS."""
from pages import settings
from pages.models import Page


def media(request):
    """Adds media-related variables to the `context`."""
    return {
        'PAGES_MEDIA_URL': settings.PAGES_MEDIA_URL,
        'PAGE_USE_SITE_ID': settings.PAGE_USE_SITE_ID,
        'PAGE_HIDE_SITES': settings.PAGE_HIDE_SITES,
        'PAGE_LANGUAGES': settings.PAGE_LANGUAGES,
    }
