======================
Page CMS reference API
======================

.. contents::
    :local:
    :depth: 1

The application model
======================

Gerbi CMS declare rather simple models: :class:`Page <django_gerbi.models.Page>`
:class:`Content <django_gerbi.models.Content>` and :class:`PageAlias <django_gerbi.models.PageAlias>`.

Those Django models have the following relations:

.. aafig::
    :aspect: 60
    :scale: 150
    :proportional:

              +------------+
              |PageAlias   |
              +-----+------+
                    |
                foreign key
                    |
                +---v---+
        +------>+ Page  +
        |       +---+---+
        |           |
        |          use
        |           |
        |     +-----v-----+       +-------+---------------+
        |     | Template 1+------>+ Placeholder Node title|
        |     +-----+-----+       +-------+---------------+
        |           |
     foreign key  contains
        |           |
        |   +-------v--------------+
        |   | Placeholder Node body|
        |   +-------+--------------+
        |           |
        |           |
        |  +--------+--------+-------------+
        |  |                 |             |
      +-+--v------+    +-----v-----+       v
      | Content   |    | Content   |     SSSSS
      | english   |    | french    |     SSSSS
      +-----------+    +-----------+


Placeholders
============

.. automodule:: django_gerbi.placeholders
    :members:
    :undoc-members:

Template tags
=============

.. automodule:: django_gerbi.templatetags.gerbi_tags
    :members:

Widgets
=======

.. automodule:: django_gerbi.widgets
    :members:
    :undoc-members:

Page Model
==========

.. autoclass:: django_gerbi.models.Page
    :members:

Page Manager
============

.. autoclass:: django_gerbi.managers.PageManager
    :members:
    :undoc-members:

Page view
==========

.. autoclass:: django_gerbi.views.Details
    :members:

Content Model
=============

.. autoclass:: django_gerbi.models.Content
    :members:
    :undoc-members:

Content Manager
===============

.. autoclass:: django_gerbi.managers.ContentManager
    :members:
    :undoc-members:

PageAlias Model
===============

.. autoclass:: django_gerbi.models.PageAlias
    :members:
    :undoc-members:

PageAlias Manager
=================

.. autoclass:: django_gerbi.managers.PageAliasManager
    :members:
    :undoc-members:

Utils
=====

.. automodule:: django_gerbi.utils
    :members:
    :undoc-members:

Http
====

.. automodule:: django_gerbi.http
    :members:
    :undoc-members:

Admin views
===========

.. automodule:: django_gerbi.admin.views
    :members:
    :undoc-members:
