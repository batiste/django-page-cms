============
 Changelog
============

This file describe new features and incompatibilites between released version of the CMS.

Release 1.9.10
================

Released the 27th of December 2016.

    * Fix a performance issue with new placeholder block parsing. :ref:`Placeholder can now be used as blocks <placeholderasblocks>`


Release 1.9.9
=============

Released the 18th of December 2016.

    * Fix a couple of problems with inline frontend editing
    * :ref:`Placeholder can now be used as blocks <placeholderasblocks>`


Release 1.9.8
=============

Released the 13th of December 2016.

    * Official support for inline frontend editing
    * New shared keyword for placeholder: shared content accross pages


Release 1.9.7
=============

Released the 23rd of October 2016.

    * Fix the build and some details in the admin
    * Improvement in the drag and drop interface

Release 1.9.6
=============

Released the 11th of September 2016.

    * Improvement in the page edit form UX

Release 1.9.5
=============

Released the 8th of September 2016.

    * Improvement in the drag and drop UX

Release 1.9.4
=============

Released the 2nd of September 2016.

    * Changes in setup.py so dependecies can be installed with `pip install django-page-cms[full]`

Release 1.9.3
=============

Released the 2nd of Semptember 2016.

    * A new conditional template tag called page_has_content
    * A new gerbi console command to create demo websites: gerbi --create mywebsite
    * Improve page admin look and feel
    * Fix problems withing the admin (Javascript errors)
    * Update documentation

Release 1.9.1
=============

Released the 12th of June 2016.

    * A new keyword section on the placeholer has been added to create groups 
      in the admin
    * Language fallback for empty page placeholders in the admin was enabeled
      and causing possible weirdness
    * Grappelli support (incomplete)
    * Support for section (grouping) fields in admin
    * Clean upload file names
    * Bug fixes
    * Basic RTE improvement in the admin
    * Code cleanup

Release 1.9.0
=============

Released the 1st of February 2016.

    * Support Django 1.9
    * Support Python 3.4, 3.5
    * Redirect to new urls after updating slug. New settings PAGE_REDIRECT_OLD_SLUG
    * Added get_pages_with_tag templatetag
    * Added tags in JSON export/import
    * Code cleanup
    * PAGE_CACHE_LOCATION setting is removed

Release 1.8.2
=============

Released the 20th of December 2015.

    * Migrations files were not included in 1.8.1
    * Add a pages_push and pages_pull command that permit to pull and push content between
      different hosts in rather smart and non breaking way.

Release 1.8.1
=============

Released the 24th of September 2015.

    * Added support for a REST API using Django Rest Framework (http://www.django-rest-framework.org/)
    * Refactoring

Release 1.8.0
=============

Released the 23rd of April 2015.

    * Updated to Django 1.8
    * Jumped 2 version to stick with Django versionning numbers

Backward Incompatible Changes
------------------------------

    * Incompatible with Django 1.7 and lower

Release 1.6.2
=============

Released the 27th of July 2014.

    * Added a ckeditor placeholder using django-ckeditor
    * The project now use transifex to handle it's translations (https://www.transifex.com/projects/p/django-page-cms-1/)
    * Fix several bugs related to placeholders and cache.
    * Fix a bug with files using non ascii characters.
    * Fix a bug with the loading icon.


Release 1.6.1
=============

Released the 2nd of June 2014.

    * Fix a bug with the image upload.
    * Fix a bug with files using non ascii characters.
    * Fix a bug with the loading icon.


Release 1.6.0
==============

Released the 11th of March 2014.

Highlights
--------------

    * Full compatibility with Python 3.3 (https://travis-ci.org/batiste/django-page-cms) as well python 2.7 with the same code base.
    * Django-page-cms is now compatible with Django 1.6.2
    * Setup selenium tests infrastructure
    * :ref:`New Markdown Placeholder  <markdownplaceholder>`
    * Django-page-cms has a test coverage of 90%. Commits that bring this number down will be rejected.
    * Preserve the language choice across saves in the admin interface
    * Move the JSON export in it's own plugin application

Backward Incompatible Changes
------------------------------

    * HTML sanitization and the dependecy to the html5lib have been removed.
    * Remove support for WYMEditor, markItUp and CKEditor editors. Rational:
      Those Widget are untested, not updated and were created when packages for those widgets didn't exists as python packages (django-ckeditor, django-wymeditor, django-markitup).
      If you need those editors please install the package and register the widget to use them directly in your templates.
    * The pages_navigation context processor has been removed. This is not useful as {% load_pages %} already load the pages_navigation variable in the context.
    * Removal of the video placeholder. Rational: Used as an example but add no real value to the CMS.
    * Removal of PageAdminWithDefaultContent. Rational: PageAdminWithDefaultContent is completly untested and can be easily reproduced in any project if necessary.
    * Move po import/export to it's own plugin application.
    * PAGE_CONNECTED_MODELS is gone. Use inline admin objects instead https://docs.djangoproject.com/en/dev/ref/contrib/admin/#inlinemodeladmin-objects

Release 1.5.3
==============

Released the 23 of October 2013.

    * Tiny MCE javascript is not included with this CMS anymore. Please use https://github.com/aljosa/django-tinymce
    * A more agressive cache should reduce page related SQL queries to 3 once the cache is warm.
    * A plugin app example as been created in pages.plugins.category.
    * jquery.query-2.1.7.js is properly restaured this time.

Release 1.5.2
==============

Released on the first of September 2013.

    * Fix bad migrations.
    * Test and fix a bug with the PAGE_AUTOMATIC_SLUG_RENAMING option.
    * Re-introduce a previously delete javascript file (jquery.query-2.1.7.js) necessary in the admin interface.
    * File and Image placeholer now use the same filename scheme that preserve the original filename.

Release 1.5.1
==============

Released on the 7th of August 2013.

    * Documentation fixes.
    * Dependencies on html5lib was incorrect.
    * Placeholder names can now be any string if quotes are used. "éà àü" is a valid placeholder name.

Release 1.5.0
==============

    * Full compatibility with Django 1.5
    * New Drag and Drop interaction in the admin (jquery.ui not needed anymore)
    * New placeholder JsonPlaceholderNode
    * New settings PAGE_IMPORT_ENABLED, PAGE_EXPORT_ENABLED and PAGE_AUTOMATIC_SLUG_RENAMING
    * Haystack 2.0 compatibility (not tested)
    * Cleanup the admin JavaScript files
    * Possibility to Substituting a custom User model (new in Django 1.5)
    * Remove the dependency on BeautifulSoup

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
      :doc:`Documentation on the commands <commands>`
    * Add a PAGE_CONTENT_REVISION_DEPTH setting to limit the amount of revision we want to keep.
    * Fix a bug so the CMS can run without django-taggit installed.
    * Fix a bug with placeholder and template inheritance.
    * The `pages-root` URL doesn't need to be specified anymore. But you can still
      use it if you want to define a special URL for the root page.


Backward Incompatible Changes
-------------------------------

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
