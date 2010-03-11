===================================
Display page's content in templates
===================================

Django page CMS provide several ready to use template tags. To use these tags in your templates
you must load them first::

    {% load pages_tags %}

.. contents::
    :local:
    :depth: 1

get_content
-----------

Store a content type from a page into a context variable that you can reuse after::

    {% get_content current_page "title" as content %}

You can also use the slug of a page::

    {% get_content "my-page-slug" "title" as content %}

You can also use the id of a page::

    {% get_content 10 "title" as content %}

.. note::

    You can use either the page object, the slug, or the id of the page.

show_content
------------

Output the content of a page directly within the template::

    {% show_content current_page "title" %}

.. note::

    You can use either the page object, the slug, or the id of the page.

get_page
------------

Retrieve a Page object and store it into a context variable that you can reuse after. Here is
an example of the use of this template tag to display a list of news::

    <h2>Latest news</h2>
    {% get_page "news" news_page %}
    <ul>
    {% for new in news_page.get_children %}
    <li>
        <h3>{{ new.title }}</h3>
        {{ new.publication_date }}
        {% show_content new body %}
    </li>
    {% endfor %}
    </ul>


.. note::

    You can use either the slug, or the id of the page.

show_absolute_url
-----------------

This tag show the absolute url of a page. The difference with the `Page.get_url_path` method is
that the template knows which language is used within the context and display the URL accordingly::

    {% show_absolute_url current_page %}

.. note::

    You can use either the page object, the slug, or the id of the page.