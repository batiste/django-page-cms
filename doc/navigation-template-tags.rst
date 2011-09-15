===============================================
How to use the various navigation template tags
===============================================

Presenting a navigational structure to the user is an common task on every website.
Django-pages-cms offers various template tags which can be used to create a site navigation menu.

.. contents::
    :local:

pages_menu
==========

The pages_menu tag displays the whole navigation tree, including all subpages.
This is useful for smaller sites which do not have a large number of pages.

Use the following snippet in your template::

    <ul>
    {% for page in pages_navigation %}
        {% pages_menu page %}
    {% endfor %}
    </ul>

The pages_menu tag uses the `pages/menu.html` template to render the navigation menu.
By default, the menu is rendered as a nested list::

    <ul>
        <li><a href="/page/1">page1</a></li>
        ...
    </ul>

You can of course change `pages/menu.html` with the Django override mechanism
to render things differently.

pages_dynamic_tree_menu
=======================

The pages_dynamic_tree_menu tag works similar to the pages_menu tag.
but instead of displaying the whole navigation structure,
only the following pages are displayed:

 * all "root" pages (pages which have no parent)
 * all parents of the current page
 * all direct children of the current page

This type of navigation is recommended if your site has a large number
of pages and/or a deep hierarchy, which is too complex or large
to be presented to the user at once.


Use the following snippet in your template::

    <ul>
    {% for page in pages_navigation %}
        {% pages_dynamic_tree_menu page %}
    {% endfor %}
    </ul>

The pages_dynamic_tree_menu tag uses the `pages/dynamic_tree_menu.html`
template to render the navigation menu. By default, the menu is rendered
as a nested list similar to the pages_menu tag.

pages_sub_menu
==============

The pages_sub_menu tag shows all the children of the root of the current page (the highest in the hierarchy).
This is typically used for a secondary navigation menu.

Use the following snippet to display a list of all the
children of the current root::

    <ul>
    {% pages_sub_menu current_page %}
    </ul>

Again, the default template `pages/sub_menu.html` will render the items as a nested,
unordered list (see above).


pages_siblings_menu
===================

The pages_siblings_menu tag shows all the children of the immediate parent of the current page. This can be used for example as a secondary menu.

Use the following snippet to display a list of all the children of the
immediate parent of the current page::

    <ul>
    {% pages_siblings_menu current_page %}
    </ul>

Again, the default template `pages/sub_menu.html` will render the items as a nested,
unordered list (see above).


pages_breadcrumb
================

With the pages_breadcrumb tag, it is possible to use the "breadcrumb"/"you are here"
navigational pattern, consisting of a list of all parents of the current page::

    {% pages_breadcrumb current_page %}

The output of the pages_breadcrumb tag is defined by the template `pages/breadcrumb.html`.

load_pages
==========

The load_pages Tag can be used to load the navigational structure
in views which are *not* rendered through page's own details() view.
It will check the current template context and adds the pages and
current_page variable to the context, if they are not present.

This is useful if you are using a common base template for your whole site,
and want the pages menu to be always present, even if the actual content
is not a page.

The load_pages does not take any parameters and must
be placed before one of the menu-rendering tags::

    {% load_pages %}
