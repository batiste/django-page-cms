===================================================================================
Django-Page-CMS to Django-Gerbi migration how-to
===================================================================================

Previously known as Django-page-CMS, the CMS is now know as Gerbi and its
Django application name is django_gerbi. This "rebranding" as some
consequence on your existing installations of the CMS. You will find
bellow instruction to guide you through the migration of your
configuration and data.

Migrate your configuration
==========================


Update your settings.py
_______________________

All setting variable names previously prefixed by ``PAGE_`` are now
prefixed by ``GERBI_`` as well as the ``PAGES_MEDIA_URL`` which
is now known as ``GERBI_MEDIA_URL``. You should update your
settings.py file subsequently.


The django application name is now ``django_gerbi`` and you must then
replace ``'pages'`` in your ``INSTALLED_APPS`` tuple by
``'django_gerbi'``.

Update your urls.py
___________________

You then must update your ``urls.py``: the pattern::

  urlpatterns = patterns('',
      ...,
      (r'^pages/', include('pages.urls')),
      ...,)

has to be replaced by::

  urlpatterns = patterns('',
      ...,
      (r'^pages/', include('djang_gerbi.urls')),
      ...,)


Migrate your templates
======================

All template tags previously prefixed by ``pages_`` are now prefixed
by ``gerbi_``. To continue using the legacy tag names you can set the
``GERBI_LEGACY_TAG_NAMES`` variable to ``True``.

Note that the legacy tag names are deprecated and will be droped in a
future release: you must not use them in new templates and should
update your existing templates.

Migrate data on your PostgreSQL server
======================================

New python django module name means new database table names. To
safely copy your pages into the new tables run the following queries,
instead of performing a classic ``python ./manage.py syncdb``::

    CREATE TABLE django_gerbi_page AS TABLE pages_page WITH DATA;
    CREATE TABLE django_gerbi_pagealias AS TABLE pages_pagealias WITH DATA;
    CREATE TABLE django_gerbi_content AS TABLE pages_content WITH DATA;
    CREATE TABLE django_gerbi_pagepermission AS TABLE pages_pagepermission WITH DATA;

Note that the old tables will not be deleted. It is your
responsability to delete them when your are shure you recovered all
your data.

If you used the standard scheme to store your templates, it is most
likely that they are stored within the
``myapp/templates/pages/``. This directory is now called
``myapp/templates/django_gerbi/`` and the pages stored in the database
hold a wrong reference to the old directory. This is typically
diagnosed by a ``TemplateDoesNotExist`` exception when you try to load
a page.  To fix the problem, you have to run the following SQL query::

    UPDATE django_gerbi_page SET template = regexp_replace ( django_gerbi_page.template, '^pages/', 'django_gerbi/') ;

Migrate data on your MySQL server
===================================


===============================================
Migrate applications on built on top of the CMS
===============================================

If you built an application on top of the CMS, reusing the models and
such, you will be happy to learn that the API has been left
untouched. So the only thing that needs to be done is to update your
``import`` s::

  import pages.some_module
  from pages import some_class, some_function

has to become::

  import django_gerbi.some_module
  from pages import some_class, some_function


