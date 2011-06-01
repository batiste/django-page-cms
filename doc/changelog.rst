============
 Changelog
============

This file describe new features and incompatibilites between released version of the CMS.

Release 1.4.3
==============

    * New placeholder tag: contactplaceholder that produce a contact form.
    * Performance improvement: don't render the template with a Context in the get_placeholder method.
    * Fix some issue with Ajax calls and csrf protection.
    * Fix some outdated migrations.
    * New placeholder tag: fileplaceholder allows users to upload files.
    * Italian traduction.
    * Added X-View headers to response in order to work with 'Edit this object' bookmarklet.

Release 1.4.2
==============

    * Fix a packaging issue with the static files. The package_data setup variable was incorrect.

Release 1.4.1
==============

    * Tests are not executed when you execute ./manage.py test, unless explicity enabled with PAGE_ENABLE_TESTS.
    * Deprecation of the auto_render decorator.
    * Fix the request mock to work with the latest trunk of Django.
    * ImagePlaceholder: use django.core.files.storage.default_storage instead of from django.core.files.storage import FileSystemStorage
    * Added setting for allowing realtime search index rather than index on management command.
    * Optimize and cache is_first_root method.
    * Fix a bug in the {% get_content %} tag.


Release 1.4.0
==============

    * A cute new name for the django page CMS : *Gerbi CMS*. The package name will remain `django-page-cms` for
      this release but might be changed to `gerbi` in a near future.
    * Implement 2 classes for the Django sitemap framework. :ref:`Documentation on sitemap classes <sitemaps>`
    * Add a markitup REST editor.
    * Fix a bug with `pages_dynamic_tree_menu` template tag and multiple roots in a pages tree.
    * Added a PAGES_STRICT_URLS setting. If set to `True` the CMS will check for the complete URL instead
      of just the slug. If the complete path doesn't match, a 404 error is raised in the view.
    * Added 2 managing commands for exporting and importing PO translation files into the CMS.
      :doc:`Documentation on the commands</commands>`
    * Add a PAGE_CONTENT_REVISION_DEPTH setting to limit the amount of revision we want to keep.
    * Fix a bug so the CMS can run without django-taggit installed.
    * Fix a bug with placeholder and template inheritance.
    * The `pages-root` URL doesn't need to be specified anymore. But you can still
      use it if you want to define a special URL for the root page.


Incompatible changes
---------------------

    * New delegation rules: the CMS delegate not only the exact path leading to the page but also
      the whole sub path. :doc:`Documentation on the delegation as been updated</3rd-party-apps>`.
    * The default view now raise an `ValueError` if the `path` argument is not passed instead
      of guessing the path by using `request.path`.


Release 1.3.0
==============

    * The default view is now a class therefor you can subclass it and change it's behavior more easily.
    * Fix a bug with get_slug_relative_path that may strip the language 2 times from the URL.
    * Remove the dependency to django-unittest-depth.
    * Don't raise a 404 when the LANGUAGE_CODE language is not present in the PAGE_LANGUAGES list.
    * Get ride of the only raw SQL command by using the ORM's annotate.
    * Fix a cache issue with show_absolute_url and get_complete_slug.
    * The default template for menu now display the title instead of the slug in the link
    * Improve the default application look.

Incompatible changes
---------------------

    * Placeholer content is now marked as safe by default.
    * The CMS need the new version of django-mptt 0.4.1.
    * Remove the support for django-tagging and use django-taggit instead.

Maintenance
-----------

Install the new django-mptt package::

    sudo pip install -U django-mptt>=0.4.1

If you want to use tags you should install the new django-taggit::

    sudo pip install django-taggit

Release 1.2.1
=============

    * Change the cache class attributes into data attributes as it was intented in
      the design for the "per instance" cache.

Release 1.2.0
=============

    * Add publish right managements in the admin.
    * Fix an admin bug with the untranslated option for placeholder.
    * Fix the package so the media are included.
    * Fix bug with the default value of PAGE_TEMPLATES doesn't trigger an error in the admin
      when unspecified.
    * Add a delete image feature to the image placeholder.
    * Make root page url '/' work with the PAGE_USE_LANGUAGE_PREFIX option.
    * Change the placeholder save prototype by adding an extra keyword parameter: extra_data.
    * Fix a bug with the image placeholder when the "save and continue" button is used.

Release 1.1.3
=============

    * Improved search index (url and title are included).
    * The setup now specify django-mptt-2 instead of django-mptt.
    * New template tag for navigation called "pages_siblings_menu".
    * New object PageAdminWithDefaultContent: copy the official language text into new
      language page's content blocks
    * New setting PAGE_HIDE_SITES to hide the sites. When True the CMS only
      show pages from the current site used to access the
      admin. This allows administration of separate page-cms sites with the same DB.
    * New admin template tag: language_content_up_to_date templatetag: mark the translations needing
      updating in the admin.
    * DEFAULT_PAGE_TEMPLATE is rennomed into PAGE_DEFAULT_TEMPLATE. This setting will still continue to work.
    * Add a new template tag get_page to insert page object into the context.

Release 1.1.2
=============

    * Change the default value of PAGE_TAGGING and PAGE_TINYMCE to `False`
    * Implement drag and drop within the admin interface.
    * Implement haystack SearchIndex for page content search.
    * Add the untranslated placeholder keyword. Enable the user to have a single
      placeholder content accross all languages.
    * Add back the hierarchical change rights management for every page.

Release 1.1.1
=============

    * Add new inherited placeholder option to inherit content from a parent page.
    * PagePermission object is gone in favor of django-authority.
    * New permission by language.
    * New permission for freezing page content.
    * Add a get_date_ordered_children_for_frontend Page's method.
    * Add missing templates to the package.

Release 1.1.0
=============

    * PAGE_TEMPLATES setting can also be a callable.
    * PAGE_UPLOAD_ROOT setting enable you to choose where files are uploaded.
    * The CMS comes with south migrations if you want to use them.
    * `get_url` is renamed into `get_complete_slug`.
    * `get_absolute_url` is renamed into `get_url_path`.
    * Admin widgets now needs to use a registery to be used within the admin.
      The placeholder template tag doesn't load load external modules for you anymore.
    * RTL support for pages in admin.
    * The context variable `pages` has been renamed to `pages_naviagtion` to avoid
      any name conflict with some pagination tags.

Maintenance
-----------

A new character field called `delegate_to` is added to the page model.
to enable the delegation of the pages rendering to a 3rd party application::

    ALTER TABLE pages_page ADD COLUMN delegate_to varchar(100) NULL;

Release 1.0.9
=============

    * Finish to migrate the old wiki into the sphinx documentation
    * Fix the package so it can be installed properly with easy_install
    * Add a new placeholder {% imageplaceholder %} for a basic automatic image
      handling in the admin.

Release 1.0.8
=============

    * A few bug fix.
    * A automatic internal link system. Page link don't break even if you move the
      linked page.
