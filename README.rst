
django-page-cms
===============

.. image:: https://badges.gitter.im/django-page-cms/Lobby.svg
   :alt: Join the chat at https://gitter.im/django-page-cms/Lobby
   :target: https://gitter.im/django-page-cms/Lobby?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge

.. image:: https://travis-ci.org/batiste/django-page-cms.svg?branch=master
  :target: https://travis-ci.org/batiste/django-page-cms

.. image:: https://coveralls.io/repos/batiste/django-page-cms/badge.svg
  :target: https://coveralls.io/r/batiste/django-page-cms
  
.. image:: https://readthedocs.org/projects/django-page-cms/badge/?version=latest
  :target: http://django-page-cms.readthedocs.io/en/latest/

.. image:: https://codeclimate.com/github/batiste/django-page-cms/badges/gpa.svg
  :target: https://codeclimate.com/github/batiste/django-page-cms
  :alt: Code Climate

.. image:: https://scrutinizer-ci.com/g/batiste/django-page-cms/badges/quality-score.png?b=master
  :target: https://scrutinizer-ci.com/g/batiste/django-page-cms/?branch=master
  :alt: Scrutinizer Code Quality

This Django CMS enables you to create and administrate hierarchical pages in a simple and powerful way.

For a quick demo.

  $ pip install django-page-cms[full]; gerbi --create mywebsite

Or with docker

  $ docker-compose up
  $ docker exec -it django-page-cms_web_1  python example/manage.py createsuperuser

More informations

  * `Install <http://django-page-cms.readthedocs.io/en/latest/installation.html>`_
  * `Full documentation <http://django-page-cms.readthedocs.io/en/latest/>`_
  * `How to contribute <doc/contributions.rst>`_

Django page CMS is based around a placeholders concept. Placeholder is a special template tag that
you use in your page templates. Every time you add a placeholder in your template such field
dynamically appears in the page admin interface.

Each page can have a different template with different placeholders.

.. image:: https://github.com/batiste/django-page-cms/raw/master/doc/images/admin-screenshot-1.png
    :width: 350px
    :align: center

