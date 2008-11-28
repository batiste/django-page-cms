"""
Convenience module for access of custom pages application settings,
which enforces default settings when the main settings module does not
contain the appropriate settings.
"""
from os.path import join
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

# Which template should be used.
DEFAULT_PAGE_TEMPLATE = getattr(settings, 'DEFAULT_PAGE_TEMPLATE', None)
if DEFAULT_PAGE_TEMPLATE is None:
    raise ImproperlyConfigured('Please make sure you specified a DEFAULT_PAGE_TEMPLATE setting.')

# Could be set to None if you don't need multiple templates.
PAGE_TEMPLATES = getattr(settings, 'PAGE_TEMPLATES', None)
if PAGE_TEMPLATES is None:
    PAGE_TEMPLATES = ()

# Whether to enable permissions.
PAGE_PERMISSION = getattr(settings, 'PAGE_PERMISSION', True)

# Whether to enable tagging. 
PAGE_TAGGING = getattr(settings, 'PAGE_TAGGING', True)

# Whether to only allow unique slugs.
PAGE_UNIQUE_SLUG_REQUIRED = getattr(settings, 'PAGE_UNIQUE_SLUG_REQUIRED', True)

# Whether to enable revisions.
PAGE_CONTENT_REVISION = getattr(settings, 'PAGE_CONTENT_REVISION', True)

# Defines which languages should be offered.
PAGE_LANGUAGES = getattr(settings, 'PAGE_LANGUAGES', settings.LANGUAGES)

# Defines which language should be used by default and falls back to LANGUAGE_CODE
PAGE_DEFAULT_LANGUAGE = getattr(settings, 'PAGE_DEFAULT_LANGUAGE', settings.LANGUAGE_CODE)[:2]

# Defines how long page content should be cached, including navigation and admin menu.
PAGE_CONTENT_CACHE_DURATION = getattr(settings, 'PAGE_CONTENT_CACHE_DURATION', 60)

# The id of default Site instance to be used for multisite purposes.
SITE_ID = getattr(settings, 'SITE_ID', 1)

# You can exclude some placeholder from the revision process
PAGE_CONTENT_REVISION_EXCLUDE_LIST = getattr(settings, 'PAGE_CONTENT_REVISION_EXCLUDE_LIST', ())

# Sanitize the user input with html5lib
PAGE_SANITIZE_USER_INPUT = getattr(settings, 'PAGE_SANITIZE_USER_INPUT', False)

# URL that handles pages' media and uses <MEDIA_ROOT>/pages by default.
PAGES_MEDIA_URL = getattr(settings, 'PAGES_MEDIA_URL', join(settings.MEDIA_URL, 'pages/'))

# Show the publication date field in the admin, allows for future dating
# Changing this from True to False could cause some weirdness.  If that is required,
# you should update your database to correct any future dated pages
PAGE_SHOW_START_DATE = getattr(settings, 'PAGE_SHOW_START_DATE', False)

# Show the publication end date field in the admin, allows for page expiration
# Changing this from True to False could cause some weirdness.  If that is required,
# you should update your database and null any pages with publication_end_date set.
PAGE_SHOW_END_DATE = getattr(settings, 'PAGE_SHOW_END_DATE', False)
