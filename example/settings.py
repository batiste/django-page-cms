# -*- coding: utf-8 -*-
# Django settings for CMS project.
import os
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

DEBUG = True

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

CACHE_BACKEND = "locmem:///?timeout=300&max_entries=6000"

MANAGERS = ADMINS

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

# this is for production
STATIC_ROOT = os.path.join(PROJECT_DIR, 'collect-static/')
STATIC_URL = '/static/'

STATICFILES_DIRS = (
  os.path.join(PROJECT_DIR, 'static/'),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)


FIXTURE_DIRS = [os.path.join(PROJECT_DIR, 'fixtures')]

SECRET_KEY = 'WARNING: set a proper secure key before going to production'

_TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.template.context_processors.i18n",
    "django.template.context_processors.debug",
    "django.template.context_processors.request",
    "django.template.context_processors.media",
    "django.contrib.messages.context_processors.messages",
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

MIDDLEWARE = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'urls'

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
    'django.contrib.humanize',
    'taggit',
    'sorl.thumbnail',
    'pages',
    'pages.plugins.jsonexport',
    'pages.plugins.pofiles',
    'mptt',
    'rest_framework',
    'haystack',
    'django.contrib.messages',
    'django.contrib.admin',
    'django.contrib.sites',
]

PAGE_TAGGING = True

# Default language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en'

# This is defined here as a do-nothing function because we can't import
# django.utils.translation -- that module depends on the settings.
gettext_noop = lambda s: s  # noqa

# languages you want to translate into the CMS.
PAGE_LANGUAGES = (
    ('en', gettext_noop('English')),
    ('de', gettext_noop('Deutsch')),
    ('fr', gettext_noop('Français')),
)

PAGE_USE_LANGUAGE_PREFIX = True

ALLOWED_HOSTS = ['0.0.0.0', '192.168.1.50', '127.0.0.1']

# You should add here all language you want to accept as valid client
# language. By default we copy the PAGE_LANGUAGES constant and add some other
# similar languages.
languages = list(PAGE_LANGUAGES)
languages.append(('fr', gettext_noop('Français')))
languages.append(('fr-be', gettext_noop('Belgium french')))
LANGUAGES = languages

PAGE_DEFAULT_TEMPLATE = 'index.html'

PAGE_TEMPLATES = (
    ('index.html', 'Default template'),
    ('blog-post.html', 'Blog post'),
    ('blog-home.html', 'Blog home'),
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

try:
    from local_settings import *  # noqa
except ImportError:
    pass
