=========================
Commands
=========================

.. contents::

Export pages content into translatable PO files
=======================================================

The pages CMS provide a command for those that would prefer
to use PO files instead of the admin inteface to translate the
pages content.

To export all the content from the published page into PO files
you can execute this Django command::

    $ python manage.py pages_export_po <path>

The files a created in the `poexport` directory if no path is provided.

After the translation is done, you can import back the changes with
another command::

    $ python manage.py pages_import_po <path>