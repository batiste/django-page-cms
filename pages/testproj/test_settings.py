# -*- coding: utf-8 -*-
# Django test settings for cms project.
import os
PROJECT_DIR = os.path.dirname(__file__)

TEST_PROJ = 'pages.testproj'

DEBUG = True
USE_TZ = True

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

CACHE_BACKEND = 'locmem:///'

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'test.db'
    }
}

# We still want to be ale to test with 1.1.X
DATABASE_ENGINE = 'sqlite3'
DATABASE_NAME = 'test.db'

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be avilable on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

MEDIA_ROOT = STATIC_ROOT = os.path.join(PROJECT_DIR, 'media')
MEDIA_URL = '/media/'

STATIC_ROOT = os.path.join(PROJECT_DIR, 'media', 'static')
STATIC_URL = MEDIA_URL + 'static/'

# Absolute path to the directory that holds pages media.
# PAGES_MEDIA_ROOT = os.path.join(STATIC_ROOT, 'pages', 'media', 'pages')
# Absolute path to the directory that holds media.
ADMIN_MEDIA_ROOT = os.path.join(STATIC_ROOT, 'admin_media')
ADMIN_MEDIA_PREFIX = '/admin_media/'


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

INTERNAL_IPS = ('127.0.0.1',)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware'
)

ROOT_URLCONF = TEST_PROJ + '.urls'

_TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_DIR, 'templates'),
)

CACHE_BACKEND = "locmem:///?timeout=300&max_entries=6000"

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.admin',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'rest_framework',
    'mptt',
    'pages',
    'taggit',
    TEST_PROJ + '.documents',
    'django.contrib.staticfiles',
    # these 2 package don't create any dependecies
    # haystack change coverage score report by importing modules
    #'haystack',
)

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
languages.append(('it-it', gettext_noop('Italian')))
LANGUAGES = languages

# This enable you to map a language(s) to another one, these languages should
# be in the LANGUAGES config
def language_mapping(lang):
    if lang.startswith('fr'):
        # serve swiss french for everyone
        return 'fr-ch'
    return lang

PAGE_LANGUAGE_MAPPING = language_mapping

PAGE_DEFAULT_TEMPLATE = 'pages/examples/index.html'

PAGE_API_ENABLED = True

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'DIRS': _TEMPLATE_DIRS,
        'OPTIONS': {
            'debug': DEBUG,
            'context_processors': _TEMPLATE_CONTEXT_PROCESSORS,
        },
    },
]

PAGE_TEMPLATES = (
    ('pages/examples/nice.html', 'nice one'),
    ('pages/examples/cool.html', 'cool one'),
    ('pages/tests/untranslated.html', 'untranslated'),
)

PAGE_SANITIZE_USER_INPUT = True

PAGE_USE_SITE_ID = True

PAGE_TAGGING = True

HAYSTACK_SITECONF = 'example.search_sites'
HAYSTACK_SEARCH_ENGINE = 'dummy'
#HAYSTACK_WHOOSH_PATH = os.path.join(PROJECT_DIR, 'whoosh_index')

COVERAGE_EXCLUDE_MODULES = (
    "pages.migrations.*",
    "pages.tests.*",
    "pages.urls",
    "pages.__init__",
    "pages.search_indexes",
    "pages.management.commands.*",
)

COVERAGE_HTML_REPORT = True
COVERAGE_BRANCH_COVERAGE = False
PAGE_ENABLE_TESTS = True

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.SHA1PasswordHasher'
]

try:
    from local_settings import *
except ImportError:
    pass
