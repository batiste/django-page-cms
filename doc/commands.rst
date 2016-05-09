=========================
Commands
=========================

.. contents::

Import and export content between diffent hosts using the API
================================================================

Gerbi CMS comes with a simple API that uses Django REST Framework. You can enable the
API by setting the PAGE_API_ENABLED in the CMS settings to `True`.

When this is done, your host should have an API at the following
address <address of your cms>/api/

Pulling data from a host: pages_pull
---------------------------------------

From example if you enabled the API on your local development instance you can do::

    $ python manage.py pages_pull staff_account_name:password
    Fetching page data on http://127.0.0.1:8000/api/
    data/download.json written to disk

The default for the host is the localhost (127.0.0.1:8000). This command accept the option `--filename` and `--host`

Pushing data to a host: pages_push
-------------------------------------

Similarly you can push the collected data to an host::

    python manage.py pages_push staff_account_name:password
    Fetching the state of the pages on the server http://127.0.0.1:8000/api/
    Update page 1 .............
    Update page 2 ....
    Update page 3 ....

This command accepts the option `--filename` and `--host`

Limitations
------------------

The push command does it's best creating and updating pages between 2 hosts but equivalency
cannot be guaranteed. Also files associated with the pages are yet
not transfered using this API.

To best syncronise 2 hosts (A:production, B: staging) first pull from A and push the content 
to B to have an accurate representation of production data.

Do your modification on B then then push back on A.


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