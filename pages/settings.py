# -*- coding: utf-8 -*-
# Convenience module that provides access to custom settings for the
# ``pages`` application.  Provides default settings for the ``pages``
# application when the project ``settings`` module does not contain
# the appropriate settings.
from os.path import join
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

# The path to default template 
DEFAULT_PAGE_TEMPLATE = getattr(settings, 'DEFAULT_PAGE_TEMPLATE', None)
if DEFAULT_PAGE_TEMPLATE is None:
    raise ImproperlyConfigured('Please make sure you specified a '
                               'DEFAULT_PAGE_TEMPLATE setting.')

# PAGE_TEMPLATES is a list of tuples that specifies the which templates 
# are available in the ``pages`` admin.  Templates should be assigned in 
# the following format:
#
# PAGE_TEMPLATES = (
#    ('pages/nice.html', 'nice one'),
#    ('pages/cool.html', 'cool one'),
# )
PAGE_TEMPLATES = getattr(settings, 'PAGE_TEMPLATES', None)
if PAGE_TEMPLATES is None:
    PAGE_TEMPLATES = ()

# Set ``PAGE_PERMISSION`` to ``False`` if you do not wish to enable 
# advanced hierarchic permissions on your pages.
PAGE_PERMISSION = getattr(settings, 'PAGE_PERMISSION', True)

# Set ``PAGE_TAGGING`` to ``False`` if you do not wish to use the 
# ``django-tagging`` application. 
PAGE_TAGGING = getattr(settings, 'PAGE_TAGGING', True)
if PAGE_TAGGING and "tagging" not in getattr(settings, 'INSTALLED_APPS', []):
    raise ImproperlyConfigured('django-tagging could not be found.\n'
                               'Please make sure you\'ve installed it '
                               'correctly or disable the tagging feature by '
                               'setting PAGE_TAGGING to False.')

# Set this to ``True`` if you wish to use the ``django-tinymce`` application.
PAGE_TINYMCE = getattr(settings, 'PAGE_TINYMCE', False)
if PAGE_TINYMCE and "tinymce" not in getattr(settings, 'INSTALLED_APPS', []):
    raise ImproperlyConfigured('django-tinymce could not be found.\n'
                               'Please make sure you\'ve installed it '
                               'correctly or disable the tinymce feature by '
                               'setting PAGE_TINYMCE to False.')

# Set ``PAGE_UNIQUE_SLUG_REQUIRED`` to ``True`` to enforce unique slug names 
# for all pages.
PAGE_UNIQUE_SLUG_REQUIRED = getattr(settings, 'PAGE_UNIQUE_SLUG_REQUIRED', 
                                    False)

# Set ``PAGE_CONTENT_REVISION`` to ``False`` to disable the recording of 
# revision information about made to pages in the database
PAGE_CONTENT_REVISION = getattr(settings, 'PAGE_CONTENT_REVISION', True)

# A list tuples that defines the languages that pages can be translated into.
#
# gettext_noop = lambda s: s
#
# PAGE_LANGUAGES = (
#    ('zh-cn', gettext_noop('Chinese Simplified')),
#    ('fr-ch', gettext_noop('Swiss french')),
#    ('en-us', gettext_noop('US English')),
#)
PAGE_LANGUAGES = getattr(settings, 'PAGE_LANGUAGES', settings.LANGUAGES)

# Defines which language should be used by default.  If 
# ``PAGE_DEFAULT_LANGUAGE`` not specified, then project 
# ``settings.LANGUAGE_CODE`` is used 
PAGE_DEFAULT_LANGUAGE = getattr(settings, 'PAGE_DEFAULT_LANGUAGE', 
                                settings.LANGUAGE_CODE)

# PAGE_LANGUAGE_MAPPING should be assigned a function that takes a single
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
# PAGE_LANGUAGE_MAPPING variable.
#
#     def language_mapping(lang):
#         if lang.startswith('zh'):
#             return 'zh-cn'
#         return lang
#     PAGE_LANGUAGE_MAPPING = language_mapping 
PAGE_LANGUAGE_MAPPING = getattr(settings, 'PAGE_LANGUAGE_MAPPING', lambda l: l)

# Set SITE_ID to the id of the default ``Site`` instance to be used on
# installations where content from a single installation is served on 
# multiple domains via the ``django.contrib.sites`` framework.
SITE_ID = getattr(settings, 'SITE_ID', 1)

# Set PAGE_USE_SITE_ID to ``True`` to make use of the ``django.contrib.sites``
# framework
PAGE_USE_SITE_ID = getattr(settings, 'PAGE_USE_SITE_ID', False)

# Set PAGE_USE_LANGUAGE_PREFIX to ``True`` to make the ``get_absolute_url``
# method to prefix the URLs with the language code
PAGE_USE_LANGUAGE_PREFIX = getattr(settings, 'PAGE_USE_LANGUAGE_PREFIX',
                                                                        False)

# Assign a list of placeholders to PAGE_CONTENT_REVISION_EXCLUDE_LIST
# to exclude them from the revision process.
PAGE_CONTENT_REVISION_EXCLUDE_LIST = getattr(settings,
    'PAGE_CONTENT_REVISION_EXCLUDE_LIST', ()
)

# Set ``PAGE_SANITIZE_USER_INPUT`` to ``True`` to sanitize the user input with
# ``html5lib``
PAGE_SANITIZE_USER_INPUT = getattr(settings, 'PAGE_SANITIZE_USER_INPUT', False)

# URL that handles pages media and uses <MEDIA_ROOT>/pages by default.
_media_url = getattr(settings, "STATIC_URL", settings.MEDIA_URL)
PAGES_MEDIA_URL = getattr(settings, 'PAGES_MEDIA_URL', join(_media_url, 'pages/'))

# Hide the slug's of the first root page ie: ``/home/`` becomes ``/``
PAGE_HIDE_ROOT_SLUG = getattr(settings, 'PAGE_HIDE_ROOT_SLUG', False)

# Show the publication start date field in the admin.  Allows for future dating
# Changing the ``PAGE_SHOW_START_DATE``  from ``True`` to ``False``
# after adding data could cause some weirdness.  If you must do this, you 
# should update your database to correct any future dated pages.
PAGE_SHOW_START_DATE = getattr(settings, 'PAGE_SHOW_START_DATE', False)

# Show the publication end date field in the admin, allows for page expiration
# Changing ``PAGE_SHOW_END_DATE`` from ``True`` to ``False`` after adding 
# data could cause some weirdness.  If you must do this, you should update 
# your database and null any pages with ``publication_end_date`` set.
PAGE_SHOW_END_DATE = getattr(settings, 'PAGE_SHOW_END_DATE', False)

# ``PAGE_CONNECTED_MODELS`` allows you to specify a model and form for this 
# model into your settings to get an automatic form to create
# and directly link a new instance of this model with your page in the admin.
#
# Here is an example:
#
# PAGE_CONNECTED_MODELS = [
#     {'model':'documents.models.Document',
#        'form':'documents.models.DocumentForm'},
# ]
#
PAGE_CONNECTED_MODELS = getattr(settings, 'PAGE_CONNECTED_MODELS', False)

# The page link filter enable a output filter on you content links. The goal
# is to transform special page class into real links at the last moment.
# This ensure that even if you have moved a page, the URL will remain correct.
PAGE_LINK_FILTER = getattr(settings, 'PAGE_LINK_FILTER', False)


# This setting is a function that can be defined if you need to pass extra
# context data to the pages templates.
PAGE_EXTRA_CONTEXT = getattr(settings, 'PAGE_EXTRA_CONTEXT', None)