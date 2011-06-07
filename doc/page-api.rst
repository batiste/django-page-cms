======================
Page CMS reference API
======================

.. contents::
    :local:
    :depth: 1

The application model
======================

Gerbi CMS declare rather simple models: :class:`Page <gerbi.models.Page>`
:class:`Content <gerbi.models.Content>` and :class:`PageAlias <gerbi.models.PageAlias>`.

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

.. automodule:: gerbi.placeholders
    :members:
    :undoc-members:

Template tags
=============

.. automodule:: gerbi.templatetags.gerbi_tags
    :members:

Widgets
=======

.. automodule:: gerbi.widgets
    :members:
    :undoc-members:

Page Model
==========

.. autoclass:: gerbi.models.Page
    :members:

Page Manager
============

.. autoclass:: gerbi.managers.PageManager
    :members:
    :undoc-members:

Page view
==========

.. autoclass:: gerbi.views.Details
    :members:

Content Model
=============

.. autoclass:: gerbi.models.Content
    :members:
    :undoc-members:

Content Manager
===============

.. autoclass:: gerbi.managers.ContentManager
    :members:
    :undoc-members:

PageAlias Model
===============

.. autoclass:: gerbi.models.PageAlias
    :members:
    :undoc-members:

PageAlias Manager
=================

.. autoclass:: gerbi.managers.PageAliasManager
    :members:
    :undoc-members:

Utils
=====

.. automodule:: gerbi.utils
    :members:
    :undoc-members:

Http
====

.. automodule:: gerbi.http
    :members:
    :undoc-members:

Admin views
===========

.. automodule:: gerbi.admin.views
    :members:
    :undoc-members:
