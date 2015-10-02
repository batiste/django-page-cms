
django-page-cms
===============

.. image:: https://travis-ci.org/batiste/django-page-cms.svg?branch=master
  :target: https://travis-ci.org/batiste/django-page-cms
  
.. image:: https://coveralls.io/repos/batiste/django-page-cms/badge.svg
  :target: https://coveralls.io/r/batiste/django-page-cms
  
.. image:: https://img.shields.io/pypi/dm/django-page-cms.svg
  :target: https://pypi.python.org/pypi/django-page-cms/
  
.. image:: https://codeclimate.com/github/batiste/django-page-cms/badges/gpa.svg
  :target: https://codeclimate.com/github/batiste/django-page-cms
  :alt: Code Climate


This Django CMS enables you to create and administrate hierarchical pages in a simple and powerful way.

  * `Full documentation <http://django-page-cms.readthedocs.org/en/latest/>`_
  * `How to contribute <doc/contributions.rst>`_

Django page CMS is based around a placeholders concept. Placeholder is a special template tag that
you use in your page templates. Every time you add a placeholder in your template such field
dynamically appears in the page admin interface.

Each page can have a different template with different placeholders.

.. image:: https://github.com/batiste/django-page-cms/raw/master/doc/admin-screenshot1.png

