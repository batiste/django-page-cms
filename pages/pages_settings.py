# django-page-cms settings
DEFAULT_PAGE_TEMPLATE = 'index.html'
# could be set to None if you don't need multiple templates
PAGE_TEMPLATES = (
    ('nice.html','nice one'), 
    ('cool.html','cool one')
)
PAGE_PERMISSION = True
PAGE_TAGGING = True
PAGE_UNIQUE_SLUG_REQUIRED = False
PAGE_CONTENT_REVISION = True
# you can exclude some placeholder from revision process
PAGE_CONTENT_REVISION_EXCLUDE_LIST = ()
PAGE_LANGUAGES = (
    ('fr', 'French version'),
    ('de', 'German Version'),
    ('en', 'English version'),
)
PAGE_CONTENT_CACHE_DURATION = 60 # page content cache, including navigation