from pages import settings

def media(request):
    """
    Adds media-related context variables to the context.
    """
    return {'PAGES_MEDIA_URL': settings.PAGES_MEDIA_URL}
