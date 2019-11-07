============
Installation
============

This document explain how to install Gerbi CMS into an existing Django project.
This document assume that you already know how to setup a Django project.

If you have any problem installing this CMS, take a look at the example application that stands in the example directory.
This application works out of the box and will certainly help you to get started.

.. contents::
    :local:
    :depth: 1

Evaluate quickly the application
=================================

Copy and paste this command in your virtual environnement and you should get a running cms instance::

    $ pip install django-page-cms[full]; gerbi --create mywebsite

Then visit http://127.0.0.1:8000/

Or use docker

    $ docker-compose up
    $ docker exec -it django-page-cms_web_1  python example/manage.py createsuperuser
    $ docker exec -it django-page-cms_web_1  python example/manage.py pages_demo

Install dependencies by using pip
==================================

The pip install is the easiest and the recommended installation method. Use::

    $ pip install django-page-cms[full]


Add django-page-cms into your INSTALLED_APPS
==================================================

To activate django-page-cms you will need to add those application::

    INSTALLED_APPS = (
        ...
        'mptt',
        'pages',
        ...
    )

Urls
====

Take a look in the ``example/urls.py`` and copy desired URLs in your own ``urls.py``.
Basically you need to have something like this::

    urlpatterns = patterns('',
        ...
        url(r'^pages/', include('pages.urls')),
        (r'^admin/', admin.site.urls),
    )

When you will visit the site the first time (``/pages/``), you will get a 404 error
because there is no published page. Go to the admin first and create and publish some pages.


Settings
========

All the Gerbi CMS specific settings and options are listed and explained in the ``pages/settings.py`` file.

Gerbi CMS require several of these settings to be set. They are marked in this document with a bold "*must*".

.. note::

    If you want a complete list of the available settings for this CMS visit
    :doc:`the list of all available settings </settings-list>`.

Default template
----------------

You *must* set ``PAGE_DEFAULT_TEMPLATE`` to the path of your default CMS template::

    PAGE_DEFAULT_TEMPLATE = 'pages/index.html'

This template must exist somewhere in your project. If you want you can copy the example templates
from the directory ``pages/templates/pages/examples/`` into the directory ``page`` of your root template directory.

Additional templates
--------------------

Optionally you can set ``PAGE_TEMPLATES`` if you want additional templates choices.
In the the example application you have actually this::

    PAGE_TEMPLATES = (
        ('pages/nice.html', 'nice one'),
        ('pages/cool.html', 'cool one'),
    )

Media directory
---------------

The django CMS come with some javascript and CSS files.
These files are standing in the ``pages/static/pages`` directory::

    $ python manage.py collecstatic pages

And the cms media files will be copied in your project's media directory.

Languages
---------

Please first read how django handle languages

* http://docs.djangoproject.com/en/dev/ref/settings/#languages
* http://docs.djangoproject.com/en/dev/ref/settings/#language-code

This CMS use the ``PAGE_LANGUAGES`` setting in order to present which language are supported by the CMS.

Django itself use the ``LANGUAGES`` setting to set the ``request.LANGUAGE_CODE`` value that is used by this CMS.
So if the language you want to support is not present in the ``LANGUAGES``
setting the ``request.LANGUAGE_CODE`` will not be set correctly.

A possible solution is to redefine ``settings.LANGUAGES``. For example you can do::

    # Default language code for this installation. All choices can be found here:
    # http://www.i18nguy.com/unicode/language-identifiers.html
    LANGUAGE_CODE = 'en'

    # This is defined here as a do-nothing function because we can't import
    # django.utils.translation -- that module depends on the settings.
    gettext_noop = lambda s: s

    # here is all the languages supported by the CMS
    PAGE_LANGUAGES = (
        ('de', gettext_noop('German')),
        ('fr', gettext_noop('Français')),
        ('en', gettext_noop('US English')),
    )

    # copy PAGE_LANGUAGES
    languages = list(PAGE_LANGUAGES)

    # redefine the LANGUAGES setting in order to be sure to have the correct request.LANGUAGE_CODE
    LANGUAGES = languages

Template context processors and Middlewares
-------------------------------------------

You *must* have this context processors into your ``TEMPLATE_CONTEXT_PROCESSORS`` setting::

    TEMPLATE_CONTEXT_PROCESSORS = (
        ...
        'pages.context_processors.media',
        ...
    )

Caching
-------

Gerbi CMS use the caching framework quite intensively. You should definitely
setting-up a cache-backend_ to have decent performance.

.. _cache-backend: http://docs.djangoproject.com/en/dev/topics/cache/#setting-up-the-cache

If you want to setup a specific cache for Gerbi CMS instead of using the default you
can do it by setting up the 'pages' cache entry::

    CACHES = {
        'default': ...
        'pages': {
            'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
            'LOCATION': '127.0.0.1:11211',
        }
    }

.. note::

    The cache has been designed with memcache in mind: a single point of truth for cache. The CMS
    invalidates the cache actively when changes are made. That means that you need a central cache if
    you run this CMS in serveral processes otherwise the caches will become inconsitent.


The sites framework
-------------------

If you want to use the `Django sites framework <http://docs.djangoproject.com/en/dev/ref/contrib/sites/#ref-contrib-sites>`_
with Gerbi CMS, you *must* define the ``SITE_ID`` and ``PAGE_USE_SITE_ID`` settings and create the appropriate Site object into the admin interface::

    PAGE_USE_SITE_ID = True
    SITE_ID = 1

The Site object should have the domain that match your actual domain (ie: 127.0.0.1:8000)


Tagging
-------

Tagging is optional and disabled by default.

If you want to use it set ``PAGE_TAGGING`` at ``True`` into your setting file and add it to your installed apps::

    INSTALLED_APPS = (
        ...
        'taggit',
        ...
    )
