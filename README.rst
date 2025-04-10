
django-page-cms
===============
  
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

.. code:: bash

  $ pip3 install "django-page-cms[full]"; gerbi --create mywebsite

Or with docker

.. code:: bash

  docker compose up web
   
To create a super user account

.. code:: bash

  docker compose run web python example/manage.py createsuperuser
   
To create a demo website

.. code:: bash

 docker compose run web python example/manage.py pages_demo

To run tests with docker

.. code:: bash

  docker compose run run-test

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

Those placeholder can also be edited inline

.. image:: https://github.com/batiste/django-page-cms/raw/master/doc/images/inline-edit.png
    :width: 350px
    :align: center



