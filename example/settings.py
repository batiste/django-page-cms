# -*- coding: utf-8 -*-
# Django settings for cms project.
import os
PROJECT_DIR = os.path.dirname(__file__)

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

CACHE_BACKEND = 'locmem:///'

MANAGERS = ADMINS

#AUTH_PROFILE_MODULE = 'profiles.Profile'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'cms.db',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be avilable on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

MEDIA_ROOT = STATIC_ROOT = os.path.join(PROJECT_DIR, 'media')
MEDIA_URL = '/media/'

STATIC_ROOT = os.path.join(PROJECT_DIR, 'static')
STATIC_URL = '/static/'


FIXTURE_DIRS = [os.path.join(PROJECT_DIR, 'fixtures')]

# Make this unique, and don't share it with anybody.
SECRET_KEY = '*xq7m@)*f2awoj!spa0(jibsrz9%c0d=e(g)v*!17y(vx0ue_3'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.i18n",
    "django.core.context_processors.debug",
    "django.core.context_processors.request",
    "django.core.context_processors.media",
    "pages.context_processors.media",
)

INTERNAL_IPS = ('127.0.0.1',)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'example.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_DIR, 'templates'),
)

#CACHE_BACKEND = "locmem:///?timeout=300&max_entries=6000"

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake'
    }
}

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    # install django-flat-theme
    'flat',
    'django.contrib.admin',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'pages.testproj.documents',
    'pages',
    #'pages.plugins.jsonexport',
    'pages.plugins.pofiles',
    'mptt',
    #'ckeditor', # if commented a fallback widget will be used
)

PAGE_TINYMCE = False
PAGE_TAGGING = False

# Default language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

# This is defined here as a do-nothing function because we can't import
# django.utils.translation -- that module depends on the settings.
gettext_noop = lambda s: s

# languages you want to translate into the CMS.
PAGE_LANGUAGES = (
    ('de', gettext_noop('German')),
    ('fr-ch', gettext_noop('Swiss french')),
    ('en-us', gettext_noop('US English')),
)

# You should add here all language you want to accept as valid client
# language. By default we copy the PAGE_LANGUAGES constant and add some other
# similar languages.
languages = list(PAGE_LANGUAGES)
languages.append(('fr-fr', gettext_noop('French')))
languages.append(('fr-be', gettext_noop('Belgium french')))
LANGUAGES = languages


PAGE_DEFAULT_TEMPLATE = 'pages/examples/index.html'


PAGE_TEMPLATES = (
    ('pages/examples/nice.html', 'nice one'),
    ('pages/examples/cool.html', 'cool one'),
    ('pages/examples/files.html', 'file upload'),
    ('pages/examples/ckeditor.html', 'ckeditor example'),
)

PAGE_SANITIZE_USER_INPUT = True

SITE_ID = 1
PAGE_USE_SITE_ID = False

# haystack dev version
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
        'PATH': os.path.join(os.path.dirname(__file__), 'whoosh_index'),
    },
}

PAGE_REAL_TIME_SEARCH = False

COVERAGE_EXCLUDE_MODULES = (
    "pages.migrations.*",
    "pages.tests.*",
    "pages.urls",
    "pages.__init__",
    "pages.search_indexes",
)
COVERAGE_HTML_REPORT = True
COVERAGE_BRANCH_COVERAGE = False

if 'ckeditor' in INSTALLED_APPS:
    CKEDITOR_UPLOAD_PATH = 'uploads'

    # ##################################
    # Your ckeditor configurations

    # Docs
    # http://docs.ckeditor.com/#!/api/CKEDITOR.config
    #
    # If some button doesn't show up, it could help to explicitly allow some
    # content related to the buttons with the allowedContent.
    # ref. http://docs.ckeditor.com/#!/guide/dev_allowed_content_rules

    CKEDITOR_CONFIGS = {
        'default': {
            'width': 600,
            'height': 300,
            #'language': 'en', # it not defined, the widget is localized with
                               # the browser default value
            'toolbar': [
                ['Bold', 'Italic','Underline', 'Strike', 'Subscript'],
                [ 'Source','-', 'Cut','Copy','Paste','PasteText','PasteFromWord'],
            ]
        },
        'minimal': {
            'width': 600,
            'toolbar': [
                ['Bold', 'Italic','Underline', 'Strike', 'Subscript', '-',
                'Link','Unlink' ],
            ],
        },
    }

try:
    from local_settings import *
except ImportError:
    pass

