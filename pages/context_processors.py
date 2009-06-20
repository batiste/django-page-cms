"""Context processors for Page CMS."""
from pages import settings

def media(request):
    """Adds media-related context variables to the context."""
    return {
        'PAGES_MEDIA_URL': settings.PAGES_MEDIA_URL,
        'PAGE_USE_SITE_ID': settings.PAGE_USE_SITE_ID
    }
