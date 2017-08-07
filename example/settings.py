# -*- coding: utf-8 -*-
# Django settings for cms project.
import os
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

DEBUG = True

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

CACHE_BACKEND = "locmem:///?timeout=300&max_entries=6000"

MANAGERS = ADMINS

# AUTH_PROFILE_MODULE = 'profiles.Profile'
LOGGING_CONFIG = None

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

MEDIA_ROOT = os.path.join(PROJECT_DIR, 'media')
MEDIA_URL = '/media/'

STATIC_ROOT = os.path.join(PROJECT_DIR, 'collect-static/')
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    # os.path.join(PROJECT_DIR, 'bootstrap'),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)


FIXTURE_DIRS = [os.path.join(PROJECT_DIR, 'fixtures')]

# Make this unique, and don't share it with anybody.
SECRET_KEY = '*xq7m@)*f2awoj!spa0(jibsrz9%c0d=e(g)v*!17y(vx0ue_3'


_TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.template.context_processors.i18n",
    "django.template.context_processors.debug",
    "django.template.context_processors.request",
    "django.template.context_processors.media",
    "pages.context_processors.media",
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'DIRS': [os.path.join(PROJECT_DIR, 'templates')],
        'OPTIONS': {
            'context_processors': _TEMPLATE_CONTEXT_PROCESSORS
        },
    },
]

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

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake'
    },
    # please use memcached in production
    'pages': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'somewhere-safe'
    }
}

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    # 'grappelli',
    'django.contrib.admin',
    'django.contrib.sites',
    'pages',
    'pages.plugins.jsonexport',
    'pages.plugins.pofiles',
    'mptt',
    'rest_framework',
    # 'ckeditor', # if commented a fallback widget will be used
    'haystack'
]

PAGE_TAGGING = False

# Default language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

# This is defined here as a do-nothing function because we can't import
# django.utils.translation -- that module depends on the settings.
gettext_noop = lambda s: s  # noqa

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


PAGE_DEFAULT_TEMPLATE = 'index.html'

PAGE_TEMPLATES = (
    ('index.html', 'Default template'),
)

PAGE_API_ENABLED = True

SITE_ID = 1
PAGE_USE_SITE_ID = True

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
            # 'language': 'en', # it not defined, the widget is localized with
            # the browser default value
            'toolbar': [
                ['Bold', 'Italic', 'Underline', 'Strike', 'Subscript'],
                ['Source', '-', 'Cut', 'Copy', 'Paste', 'PasteText', 'PasteFromWord'],
            ]
        },
        'minimal': {
            'width': 600,
            'toolbar': [
                ['Bold', 'Italic', 'Underline', 'Strike', 'Subscript', '-',
                 'Link', 'Unlink'],
            ],
        },
    }

try:
    from local_settings import *  # noqa
except ImportError:
    pass
