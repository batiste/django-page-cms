===============================================
How to use the various navigation template tags
===============================================

Presenting a navigational structure to the user is an common task on every website.
Gerbi CMS offers various template tags which can be used to create a site navigation menu.

.. contents::
    :local:

gerbi_menu
=================

The gerbi_menu tag displays the whole navigation tree, including all subpages.
This is useful for smaller sites which do not have a large number of pages.

Use the following snippet in your template::

    <ul>
    {% for page in pages_navigation %}
        {% gerbi_menu page %}
    {% endfor %}
    </ul>

The gerbi_menu tag uses the `gerbi/menu.html` template to render the navigation menu.
By default, the menu is rendered as a nested list::

    <ul>
        <li><a href="/page/1">page1</a></li>
        ...
    </ul>

You can of course change `gerbi/menu.html` with the Django override mechanism
to render things differently.

gerbi_dynamic_tree_menu
==============================

The gerbi_dynamic_tree_menu tag works similar to the gerbi_menu tag.
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
        {% gerbi_dynamic_tree_menu page %}
    {% endfor %}
    </ul>

The gerbi_dynamic_tree_menu tag uses the `gerbi/dynamic_tree_menu.html`
template to render the navigation menu. By default, the menu is rendered
as a nested list similar to the gerbi_menu tag.

gerbi_sub_menu
=====================

The gerbi_sub_menu tag shows all the children of the root of the current page (the highest in the hierarchy).
This is typically used for a secondary navigation menu.

Use the following snippet to display a list of all the
children of the current root::

    <ul>
    {% gerbi_sub_menu current_page %}
    </ul>

Again, the default template `gerbi/sub_menu.html` will render the items as a nested,
unordered list (see above).


gerbi_children_menu
==========================

The gerbi_children_menu tag shows all the direct children of the given page. Unlike the gerbi_menu tag
it is not recursive: the children's children and so on, are not displayed.
This is typically used for a secondary navigation menu.

Use the following snippet to display a list of all the
children of the current root::

    <ul>
    {% gerbi_children_menu page %}
    </ul>

Again, the default template `gerbi/sub_menu.html` will render the items as an
unordered list (see above).

gerbi_siblings_menu
==========================

The gerbi_siblings_menu tag shows all the children of the immediate parent of the current page. This can be used for example as a secondary menu.

Use the following snippet to display a list of all the children of the
immediate parent of the current page::

    <ul>
    {% gerbi_siblings_menu current_page %}
    </ul>

Again, the default template `gerbi/sub_menu.html` will render the items as a nested,
unordered list (see above).


gerbi_breadcrumb
=======================

With the gerbi_breadcrumb tag, it is possible to use the "breadcrumb"/"you are here"
navigational pattern, consisting of a list of all parents of the current page::

    <ul>
    {% gerbi_breadcrumb current_page %}
    </ul>

The output of the gerbi_breadcrumb tag is defined by the template `gerbi/breadcrumb.html`.

load_pages
==========

The load_pages Tag can be used to load the navigational structure
in views which are *not* rendered through page's own details() view.
It will check the current template context and adds the pages and
current_page variable to the context, if they are not present.

This is useful if you are using a common base template for your whole site,
and want the gerbi_menu to be always present, even if the actual content
is not a page.

The load_pages does not take any parameters and must
be placed before one of the menu-rendering tags::

    {% load_pages %}


===========================================================
Creating/Editing templates for the navigation template tags
===========================================================

The templates tags are rendered in the same context as the template they are in, but with a few additionnal variables.

Templates for gerbi_*_menu tags
======================================

The gerbi_*_menu templates tags context has the two additional variables:

 * page: the page argument given to the tag;
 * children: the children pages of the given page;

You can use them as follows::

   <h1>Topic {% show_content page 'title' %}</h1>
   <p>as the following sub topics: </p>
   <ul>
     {% for child in children %}
       <li> <a href="{% get_a%}">{% show_content child 'title' %}</a></li>
     {% endfor %}
   </ul>

See also the provided `gerbi/menu.html` and `gerbi/sub_menu.html` templates.

Templates for the gerbi_breadcrumb tag
=============================================

The page_breadcrumb template tag context has the following additional variables:

 * page: the page argument given to the tag;
 * page_navigation: the breadcrumb pages on the path to page (excluding page itself);

You can use them as follows::

  {% for parent in page_navigation %}
    &gt;&nbsp;<a href="{% show_absolute_url parent %}">{% show_content parent 'title' %}</a>&nbsp;
  {% endfor %}
  &gt;&nbsp; {% show_content page 'title' %}

See also the provided `gerbi/breadcrumb.html` templates.

