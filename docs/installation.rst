============
Installation
============

This document explain how to install django page CMS into an existing Django project.
This document assume that you already know how to setup a Django project.

If you have any problem installing this CMS, take a look at the example application that stands in the example directory.
This application works out of the box and will certainly help you to get started.

Step by step installation
=========================

For a step by step installation there is complete OpenOffice document : http://django-page-cms.googlegroups.com/web/gpc-install-instructions.odt

Install by using pip
====================

The pip install is the easiest and the recommended installation method. Use::

    sudo easy_install pip
    wget -c http://django-page-cms.googlecode.com/svn/trunk/requirements/external_apps.txt
    sudo pip install -r external_apps.txt

Every package listed in the ``external_app.txt`` should be downloaded and installed.

Install by using easy_install
=============================

On debian linux you can do::

    sudo easy_install django
    sudo easy_install html5lib
    sudo easy_install django-page-cms

* Tagging must be installed by hand or with subversion because the available package is not
  compatible with django 1.0.

* Django-mptt must be installed by hand or with subversion because the available package is not compatible with django 1.0.

Install by using subversion externals
=====================================

You can also use the trunk version of the Django Page CMS by using subversion externals::


    $ svn pe svn:externals .
    pages                   http://django-page-cms.googlecode.com/svn/trunk/pages
    mptt                    http://django-mptt.googlecode.com/svn/trunk/mptt
    tagging                 http://django-tagging.googlecode.com/svn/trunk/tagging

Urls
====

Take a look in the ``example/urls.py`` and copy desired URLs in your own ``urls.py``.
Basically you need to have something like this::

    urlpatterns = patterns('',
        ...
        url(r'^pages/', include('pages.urls')),
        (r'^admin/(.*)', admin.site.root),
    )

When you will visit the site the first time (``/pages/``), you will get a 404 error
because there is no published page. Go to the admin first and create and publish some pages.

You will certainly want to activate the static file serve view in your ``urls.py`` if you are in developement mode::

    if settings.DEBUG:
        urlpatterns += patterns('',
            # Trick for Django to support static files (security hole: only for Dev environement! remove this on Prod!!!)
            url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
            url(r'^admin_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.ADMIN_MEDIA_ROOT}),
        )

Settings
========

All the Django page CMS specific settings and options are listed and explained in the ``pages/settings.py`` file.

Django page CMS require several of these settings to be set. They are marked in this document with a bold "*must*". 

Tagging
-------

Tagging is optional and disabled by default. 

If you want to use it set ``PAGE_TAGGING`` at ``True`` into your setting file and add it to your installed apps::

    INSTALLED_APPS = (
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.admin',
        'django.contrib.sites',
        'mptt',
        'tagging',
        'pages',
        ...
    )

Caching
-------

Django page CMS use the caching framework quite intensively. You should definitely
setting-up a cache-backend_ to have decent performance.

.. _cache-backend: http://docs.djangoproject.com/en/dev/topics/cache/#setting-up-the-cache

If you cannot setup memcache or a database cache, you can use the local memory cache this way::

    CACHE_BACKEND = "locmem:///?max_entries=5000"

Languages
---------

Please first read how django handle languages

* http://docs.djangoproject.com/en/dev/ref/settings/#languages
* http://docs.djangoproject.com/en/dev/ref/settings/#language-code

This CMS use the ``PAGE_LANGUAGES`` setting in order to present which language are supported by the CMS.
By default ``PAGE_LANGUAGES`` value is set to ``settings.LANGUAGES`` value.
So you can directly set the ``LANGUAGES`` setting if you want.
In any case *you should set* ``PAGE_LANGUAGES`` or ``LANGUAGES``
yourself because by default the ``LANGUAGES`` list is big.

Django use ``LANGUAGES`` setting to set the ``request.LANGUAGE_CODE`` value that is used by this CMS. So if the language you want to support is not present in the ``LANGUAGES`` setting the ``request.LANGUAGE_CODE`` will not be set correctly.

A possible solution is to redefine ``settings.LANGUAGES``. For example you can do::

    # Default language code for this installation. All choices can be found here:
    # http://www.i18nguy.com/unicode/language-identifiers.html
    LANGUAGE_CODE = 'en-us'

    # This is defined here as a do-nothing function because we can't import
    # django.utils.translation -- that module depends on the settings.
    gettext_noop = lambda s: s

    # here is all the languages supported by the CMS
    PAGE_LANGUAGES = (
        ('de', gettext_noop('German')),
        ('fr-ch', gettext_noop('Swiss french')),
        ('en-us', gettext_noop('US English')),
    )

    # copy PAGE_LANGUAGES
    languages = list(PAGE_LANGUAGES)
    
    # All language accepted as a valid client language
    languages.append(('fr-fr', gettext_noop('French')))
    languages.append(('fr-be', gettext_noop('Belgium french')))
    # redefine the LANGUAGES setting in order to set request.LANGUAGE_CODE correctly
    LANGUAGES = languages

Template context processors and Middlewares
-------------------------------------------

You *must* have these context processors into your ``TEMPLATE_CONTEXT_PROCESSORS`` setting::

    TEMPLATE_CONTEXT_PROCESSORS = (
        'django.core.context_processors.auth',
        'django.core.context_processors.i18n',
        'django.core.context_processors.debug',
        'django.core.context_processors.media',
        'django.core.context_processors.request',
        'pages.context_processors.media',
        ...
    )

You *must* have these middleware into your ``MIDDLEWARE_CLASSES`` setting::

    MIDDLEWARE_CLASSES = (
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.middleware.doc.XViewMiddleware',
        'django.middleware.locale.LocaleMiddleware',
        ...
    )

Default template
----------------

You *must* set ``DEFAULT_PAGE_TEMPLATE`` to the name of your default CMS template::

    DEFAULT_PAGE_TEMPLATE = 'pages/index.html'

And you *must* copy the directory ``example/templates/pages`` into your root template directory.

Additional templates
--------------------

Optionally you can set ``PAGE_TEMPLATES`` if you want additional templates choices.
In the the example application you have actually this::

    PAGE_TEMPLATES = (
        ('pages/nice.html', 'nice one'),
        ('pages/cool.html', 'cool one'),
    )

The sites framework
-------------------

If you want to use the http://docs.djangoproject.com/en/dev/ref/contrib/sites/#ref-contrib-sites Django sites framework] with django-page-cms, you *must* define the ``SITE_ID`` and ``PAGE_USE_SITE_ID`` settings and create the appropriate Site object into the admin interface::

    PAGE_USE_SITE_ID = True
    SITE_ID = 1

The Site object should have the domain that match your actual domain (ie: 127.0.0.1:8000)

Media directory
---------------

The django CMS come with some javascript and CSS files. These files are standing in the ``pages/media/pages`` directory.

If you don't know how to serve static files with Django please read :

http://docs.djangoproject.com/en/dev/howto/static-files/

 
Django CMS has a special setting called ``PAGES_MEDIA_URL`` that enable you to change
how the browser will ask for these files in the CMS admin. By default the value of ``PAGES_MEDIA_URL`` is set to ::

    PAGES_MEDIA_URL = getattr(settings, 'PAGES_MEDIA_URL', join(settings.MEDIA_URL, 'pages/'))

Or in a simpler way::


    PAGES_MEDIA_URL = settings.MEDIA_URL + "pages/"


In the CMS admin template you have::


    <link rel="stylesheet" type="text/css" href="{{ PAGES_MEDIA_URL }}css/pages.css" />
    <script type="text/javascript" src="{{ PAGES_MEDIA_URL }}javascript/jquery.js"></script>


That will be rendered by default like this if ``MEDIA_URL == '/media/'``::


    <link rel="stylesheet" type="text/css" href="/media/pages/css/pages.css" />
    <script type="text/javascript" src="/media/pages/javascript/jquery.js"></script>

You can off course redefine this variable in your setting file if you are not happy with this default

In any case you must at least create a symbolic link or copy the directory ``pages/media/pages/`` into
your media directory to have a fully functioning administration interface.

The example application take another approch by directly
point the ``MEDIA_ROOT`` of the project on the ``page/media`` directory::

    # Absolute path to the directory that holds media.
    MEDIA_ROOT = os.path.join(PROJECT_DIR, '../pages/media/')
    ADMIN_MEDIA_ROOT = os.path.join(PROJECT_DIR, '../admin_media/')
    MEDIA_URL = '/media/'
    ADMIN_MEDIA_PREFIX = '/admin_media/'

But you certainly want to redefine these variables to your own project media directory.