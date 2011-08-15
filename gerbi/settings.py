# -*- coding: utf-8 -*-
"""Convenience module that provides default settings for the ``gerbi``
application when the project ``settings`` module does not contain
the appropriate settings."""
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

url = 'http://packages.python.org/django-page-cms/settings-list.html#%s'


def get_setting(*args, **kwargs):
    """Get a setting and raise an appropriate user friendly error if
    the setting is not found."""
    for name in args:
        if hasattr(settings, name):
            return getattr(settings, name)
    if kwargs.get('raise_error', False):
        setting_url = url % args[0].lower().replace('_', '-')
        raise ImproperlyConfigured('Please make sure you specified at '
            'least one of these settings: %s \r\nDocumentation: %s'
            % (args, setting_url))
    return kwargs.get('default_value', None)


# The path to default template
GERBI_DEFAULT_TEMPLATE = get_setting('GERBI_DEFAULT_TEMPLATE',
    'DEFAULT_GERBI_TEMPLATE', raise_error=True)

# GERBI_TEMPLATES is a list of tuples that specifies the which templates
# are available in the ``gerbi`` admin.  Templates should be assigned in
# the following format:
#
# GERBI_TEMPLATES = (
#    ('gerbi/nice.html', 'nice one'),
#    ('gerbi/cool.html', 'cool one'),
# )
#
# One can also assign a callable (which should return the tuple) to this
# variable to achieve dynamic template list e.g.:
#
# def _get_templates():
#    ...
#
# GERBI_TEMPLATES = _get_templates

GERBI_TEMPLATES = get_setting('GERBI_TEMPLATES',
    default_value=())


def get_page_templates():
    """The callable that is used by the CMS."""
    if callable(GERBI_TEMPLATES):
        return GERBI_TEMPLATES()
    else:
        return GERBI_TEMPLATES

# Set ``GERBI_TAGGING`` to ``False`` if you do not wish to use the
# ``django-taggit application.
GERBI_TAGGING = getattr(settings, 'GERBI_TAGGING', False)
if GERBI_TAGGING and "taggit" not in getattr(settings, 'INSTALLED_APPS', []):
    raise ImproperlyConfigured('django-taggit could not be found.\n'
                               'Please make sure you\'ve installed it '
                               'correctly or disable the tagging feature by '
                               'setting GERBI_TAGGING to False.')

# Set this to ``True`` if you wish to use the ``django-tinymce`` application.
GERBI_TINYMCE = getattr(settings, 'GERBI_TINYMCE', False)
if GERBI_TINYMCE and "tinymce" not in getattr(settings, 'INSTALLED_APPS', []):
    raise ImproperlyConfigured('django-tinymce could not be found.\n'
                               'Please make sure you\'ve installed it '
                               'correctly or disable the tinymce feature by '
                               'setting GERBI_TINYMCE to False.')

# Set ``GERBI_UNIQUE_SLUG_REQUIRED`` to ``True`` to enforce unique slug names
# for all pages.
GERBI_UNIQUE_SLUG_REQUIRED = getattr(settings, 'GERBI_UNIQUE_SLUG_REQUIRED',
                                    False)

# Set ``GERBI_CONTENT_REVISION`` to ``False`` to disable the recording of
# pages revision information in the database
GERBI_CONTENT_REVISION = getattr(settings, 'GERBI_CONTENT_REVISION', True)

# Define the number of revisions too keep in the database. Set to None
# if you want to keep everything
GERBI_CONTENT_REVISION_DEPTH = getattr(settings,
    'GERBI_CONTENT_REVISION_DEPTH', 10)

# A list tuples that defines the languages that pages can be translated into.
#
# gettext_noop = lambda s: s
#
# GERBI_LANGUAGES = (
#    ('zh-cn', gettext_noop('Chinese Simplified')),
#    ('fr-ch', gettext_noop('Swiss french')),
#    ('en-us', gettext_noop('US English')),
#)

GERBI_LANGUAGES = get_setting('GERBI_LANGUAGES', raise_error=True)

# Defines which language should be used by default.  If
# ``GERBI_DEFAULT_LANGUAGE`` not specified, then project's
# ``settings.LANGUAGE_CODE`` is used

GERBI_DEFAULT_LANGUAGE = get_setting('GERBI_DEFAULT_LANGUAGE',
    'LANGUAGE_CODE', raise_error=True)

# Extra Page permission for freezing pages and manage languages

extra = [
    ('can_freeze', 'Can freeze page',),
    ('can_publish', 'Can publish page',),
]
for lang in GERBI_LANGUAGES:
    extra.append(
        ('can_manage_' + lang[0].replace('-', '_'),
        'Manage' + ' ' + lang[1])
    )

GERBI_EXTRA_PERMISSIONS = getattr(settings, 'GERBI_EXTRA_PERMISSIONS', extra)

# GERBI_LANGUAGE_MAPPING should be assigned a function that takes a single
# argument, the language code of the incoming browser request.  This function
# maps the incoming client language code to another language code, presumably
# one for which you have translation strings.  This is most useful if your
# project only has one set of translation strings for a language like Chinese,
# which has several variants like ``zh-cn``, ``zh-tw``, ``zh-hk`, etc., but
# you want to provide your Chinese translations to all Chinese browsers, not
# just those with the exact ``zh-cn``
# locale.
#
# Enable that behavior here by assigning the following function to the
# GERBI_LANGUAGE_MAPPING variable.
#
#     def language_mapping(lang):
#         if lang.startswith('zh'):
#             return 'zh-cn'
#         return lang
#     GERBI_LANGUAGE_MAPPING = language_mapping
GERBI_LANGUAGE_MAPPING = getattr(settings, 'GERBI_LANGUAGE_MAPPING', lambda l: l)

# Set SITE_ID to the id of the default ``Site`` instance to be used on
# installations where content from a single installation is served on
# multiple domains via the ``django.contrib.sites`` framework.
SITE_ID = getattr(settings, 'SITE_ID', 1)

# Set GERBI_USE_SITE_ID to ``True`` to make use of the ``django.contrib.sites``
# framework
GERBI_USE_SITE_ID = getattr(settings, 'GERBI_USE_SITE_ID', False)

# Set GERBI_HIDE_SITES to make the sites that appear uneditable and only allow
# editing and creating of pages on the current site
GERBI_HIDE_SITES = getattr(settings, 'GERBI_HIDE_SITES', False)

# Set GERBI_USE_LANGUAGE_PREFIX to ``True`` to make the ``get_absolute_url``
# method to prefix the URLs with the language code
GERBI_USE_LANGUAGE_PREFIX = getattr(settings, 'GERBI_USE_LANGUAGE_PREFIX',
                                                                        False)

# Set this to True to raise an error 404 if the used URL path is
# not strictly the same than the page.
# This value is chanched to True by default in gerbi 1.5
GERBI_USE_STRICT_URL = getattr(settings, 'GERBI_USE_STRICT_URL', True)

# Assign a list of placeholders to GERBI_CONTENT_REVISION_EXCLUDE_LIST
# to exclude them from the revision process.
GERBI_CONTENT_REVISION_EXCLUDE_LIST = getattr(settings,
    'GERBI_CONTENT_REVISION_EXCLUDE_LIST', ()
)

# Set ``GERBI_SANITIZE_USER_INPUT`` to ``True`` to sanitize the user input with
# ``html5lib``
GERBI_SANITIZE_USER_INPUT = getattr(settings, 'GERBI_SANITIZE_USER_INPUT', False)

# URL that handles gerbi media and uses <STATIC_URL>/gerbi by default.
GERBI_MEDIA_URL = get_setting('GERBI_MEDIA_URL')
if not GERBI_MEDIA_URL:
    media_url = get_setting('STATIC_URL', 'MEDIA_URL', raise_error=True)
    GERBI_MEDIA_URL = str(media_url) + 'gerbi/'

# Hide the slug's of the first root page ie: ``/home/`` becomes ``/``
GERBI_HIDE_ROOT_SLUG = getattr(settings, 'GERBI_HIDE_ROOT_SLUG', False)

# Show the publication start date field in the admin.  Allows for future dating
# Changing the ``GERBI_SHOW_START_DATE``  from ``True`` to ``False``
# after adding data could cause some weirdness.  If you must do this, you
# should update your database to correct any future dated pages.
GERBI_SHOW_START_DATE = getattr(settings, 'GERBI_SHOW_START_DATE', False)

# Show the publication end date field in the admin, allows for page expiration
# Changing ``GERBI_SHOW_END_DATE`` from ``True`` to ``False`` after adding
# data could cause some weirdness.  If you must do this, you should update
# your database and null any gerbi with ``publication_end_date`` set.
GERBI_SHOW_END_DATE = getattr(settings, 'GERBI_SHOW_END_DATE', False)

# ``GERBI_CONNECTED_MODELS`` allows you to specify a model and form for this
# model into your settings to get an automatic form to create
# and directly link a new instance of this model with your page in the admin.
#
# Here is an example:
#
# GERBI_CONNECTED_MODELS = [
#     {'model':'documents.models.Document',
#        'form':'documents.models.DocumentForm'},
# ]
#
GERBI_CONNECTED_MODELS = getattr(settings, 'GERBI_CONNECTED_MODELS', False)

# The page link filter enable a output filter on you content links. The goal
# is to transform special page class into real links at the last moment.
# This ensure that even if you have moved a page, the URL will remain correct.
GERBI_LINK_FILTER = getattr(settings, 'GERBI_LINK_FILTER', False)

# This setting is a function that can be defined if you need to pass extra
# context dict to the pages templates. You can customize the way the function
# is called by subclassing ``gerbi.views.Details``.
GERBI_EXTRA_CONTEXT = getattr(settings, 'GERBI_EXTRA_CONTEXT', None)

# This setting is the name of a sub-folder where uploaded content, like
# placeholder images, is placed.
GERBI_UPLOAD_ROOT = getattr(settings, 'GERBI_UPLOAD_ROOT', 'upload')

# Disable the tests by default so they don't execute when the user
# execute manage.py test
GERBI_ENABLE_TESTS = getattr(settings, 'GERBI_ENABLE_TESTS', False)

# Enable use of legacy template tag names (prefixed by ``pages_``) as well as new
# ``gerbi_*`̀` template tags names.

GERBI_LEGACY_TAG_NAMES = getattr(settings, 'GERBI_LEGACY_TAG_NAMES', True)

# Enable a real time page indexation
GERBI_REAL_TIME_SEARCH = getattr(settings, 'GERBI_REAL_TIME_SEARCH', False)

