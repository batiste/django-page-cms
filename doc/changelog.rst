============
 Changelog
============

This file describe new features and incompatibilites between released version of the CMS.

Release 1.2.0
=============

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
