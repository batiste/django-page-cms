============
Introduction
============

Gerbi CMS enable you to create and administrate hierarchical pages in a simple and powerful way.

Gerbi CMS is based around a placeholders concept. A placeholder is a template tag that
you can use in your page's templates. Every time you add a placeholder in your template  a field
dynamically appears in the page admin.

The project code repository is found at this address: http://github.com/batiste/django-page-cms

.. contents::
    :local:
    :depth: 1

Screenshot
============

.. image:: admin-screenshot1.png

Key features
============

  * :doc:`Automatic creation of localized placeholders </placeholders>`
    (content area) in admin by adding placeholders tags into page templates.
  * Django admin application integration.
  * Multilingual support.
  * `Search indexation with Django haystack <http://haystacksearch.org/>`_.
  * Fine grained rights management (publisher, hierarchy manager, language manager).
  * :ref:`Rich Text Editors <placeholder-widgets-list>` are directly available.
  * Page can be moved in the tree in a visual way.
  * The tree can be expanded/collapsed. A cookie remember your preferences.
  * Possibility to specify a different page URL for each language.
  * Directory-like page hierarchy (page can have the same name if they are not in the same directory).
  * Every page can have multiple alias URLs. It's especially useful to migrate websites.
  * :doc:`Possibility to integrate 3th party apps </3rd-party-apps>`.


Other features
==============

Here is the list of features you can enable/disable:

  * Revisions,
  * Image placeholder,
  * Support for future publication start/end date,
  * Page redirection to another page,
  * Page tagging,
  * `Sites framework <http://docs.djangoproject.com/en/dev/ref/contrib/sites/#ref-contrib-sites>`_

Dependencies & Compatibility
============================

  * Django 1.8
  * Python 2.7, 3.3
  * `django-haystack if used <http://haystacksearch.org/>`_
  * `django-authority for per object rights management <http://bitbucket.org/jezdez/django-authority/src/>`_.
  * `django-mptt <http://github.com/batiste/django-mptt/>`_
  * `django-taggit <http://http://github.com/alex/django-taggit>`_ (if PAGE_TAGGING = True)
  * Gerbi CMS is shipped with jQuery.
  * Compatible with MySQL, PostgreSQL, SQLite3, some issues are known with Oracle.

.. note::

    For install instruction go to the :doc:`Installation section </installation>`

How to contribute
==================

:doc:`Contributions section </contributions>`

Report a bug
============

`Github issues <https://github.com/batiste/django-page-cms/issues>`_


Internationalisation
====================

This application is available in English, German, French, Spanish, Danish, Russian and Hebrew.

`We use transifex <https://www.transifex.com/batiste/django-page-cms-1/>`_



