======================
Page CMS reference API
======================

.. contents::
    :local:
    :depth: 1

The application model
======================

Django page CMS declare rather simple models: :class:`Page <pages.models.Page>`
:class:`Content <pages.models.Content>` and :class:`PageAlias <pages.models.PageAlias>`.

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

.. automodule:: pages.placeholders
    :members:
    :undoc-members:

Template tags
=============

.. automodule:: pages.templatetags.pages_tags
    :members:

Widgets
=======

.. automodule:: pages.widgets
    :members:
    :undoc-members:

Page Model
==========

.. autoclass:: pages.models.Page
    :members:

Page Manager
============

.. autoclass:: pages.managers.PageManager
    :members:
    :undoc-members:

Page view
==========

.. autoclass:: pages.views.Details
    :members:

Content Model
=============

.. autoclass:: pages.models.Content
    :members:
    :undoc-members:

Content Manager
===============

.. autoclass:: pages.managers.ContentManager
    :members:
    :undoc-members:

PageAlias Model
===============

.. autoclass:: pages.models.PageAlias
    :members:
    :undoc-members:

PageAlias Manager
=================

.. autoclass:: pages.managers.PageAliasManager
    :members:
    :undoc-members:

Utils
=====

.. automodule:: pages.utils
    :members:
    :undoc-members:

Http
====

.. automodule:: pages.http
    :members:
    :undoc-members:

Admin views
===========

.. automodule:: pages.admin.views
    :members:
    :undoc-members: