===================================
Display page's content in templates
===================================

Django page CMS provide several, ready to use, template tags. To load these tags you must load them first::

    {% load pages_tags %}

get_content
-----------

Store a content type from a page into a context variable that you can reuse after::

    {% get_content current_page "title" as content %}

You can also use the slug of a page::

    {% get_content "my-page-slug" "title" as content %}

You can also use the id of a page::

    {% get_content 10 "title" as content %}

In any of the content retrieval you can use either the page object, the slug,
or the id of the page.

show_content
-----------

Output the content of a page directly within the template::

    {% show_content current_page "title" %}


show_absolute_url
-----------------

Show the absolute url of a page in the right language::

    {% show_absolute_url current_page %}

page_menu
---------

Render a navigation nested list of all children of the given page::

    {% pages_menu page %}

You can override the template `pages/menu.html` if you need more control
on the rendering of this menu.

page_sub_menu
-------------

Get the root page (the highest in the hierarchy) of the given page and render
a navigation nested list of all root's children pages. This is typically used
for a secondary menu that is always open::
    
    {% pages_sub_menu page %}

You can override the template `pages/sub_menu.html` if you need more
control on the rendering of this menu.