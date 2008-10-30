"""
Convenience module for access of custom pages application settings,
which enforces default settings when the main settings module does not
contain the appropriate settings.
"""
from django.conf import settings

# Which template should be used.
DEFAULT_PAGE_TEMPLATE = getattr(settings, 'DEFAULT_PAGE_TEMPLATE', 'index.html')

# Could be set to None if you don't need multiple templates.
PAGE_TEMPLATES = getattr(settings, 'PAGE_TEMPLATES', (
    ('nice.html', 'nice one'),
    ('cool.html', 'cool one'),
))

# Whether to enable permissions.
PAGE_PERMISSION = getattr(settings, 'PAGE_PERMISSION', True)

# Whether to enable tagging. 
PAGE_TAGGING = getattr(settings, 'PAGE_TAGGING', True)

# Whether to only allow unique slugs.
PAGE_UNIQUE_SLUG_REQUIRED = getattr(settings, 'PAGE_UNIQUE_SLUG_REQUIRED', False)

# Whether to enable revisions.
PAGE_CONTENT_REVISION = getattr(settings, 'PAGE_CONTENT_REVISION', True)

# Defines which languages should be offered.
PAGE_LANGUAGES = getattr(settings, 'PAGE_LANGUAGES', settings.LANGUAGES)

# Defines how long page content should be cached, including navigation.
PAGE_CONTENT_CACHE_DURATION = getattr(settings, 'PAGE_CONTENT_CACHE_DURATION', 60)

# The id of default Site instance to be used for multisite purposes.
SITE_ID = getattr(settings, 'SITE_ID', 1)

# You can exclude some placeholder from revision process
PAGE_CONTENT_REVISION_EXCLUDE_LIST = getattr(settings, 'PAGE_CONTENT_REVISION_EXCLUDE_LIST', ())

# Sanitize the user input with html5lib
PAGE_SANITIZE_USER_INPUT = getattr(settings, 'PAGE_SANITIZE_USER_INPUT', True)
