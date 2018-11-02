===================================
Display page's content in templates
===================================

Gerbi CMS provide several template tags to extract data from the CMS.
To use these tags in your templates you must load them first:

.. code-block:: html+django

    {% load pages_tags %}

.. contents::
    :local:
    :depth: 2

get_content
-----------

Store a content type from a page into a context variable that you can reuse after:

.. code-block:: html+django

    {% get_content current_page "title" as content %}

You can also use the slug of a page:

.. code-block:: html+django

    {% get_content "my-page-slug" "title" as content %}

You can also use the id of a page:

.. code-block:: html+django

    {% get_content 10 "title" as content %}

.. note::

    You can use either the page object, the slug, or the id of the page.

show_content
------------

Output the content of a page directly within the template:

.. code-block:: html+django

    {% show_content current_page "title" %}

.. note::

    You can use either the page object, the slug, or the id of the page.

page_has_content
----------------

Conditional tag that only renders its nodes if the page
has content for a particular content type. By default the
current page is used.

Syntax:

.. code-block:: html+django

    {% page_has_content <content_type> [<page var name>] %}
        ...
    {% end page_has_content %}

Example:

.. code-block:: html+django

    {% page_has_content 'header-image' %}
        <img src="{{ MEDIA_URL }}{% imageplaceholder 'header-image' %}">
    {% end_page_has_content %}


get_page
------------

Retrieve a Page object and store it into a context variable that you can reuse after. Here is
an example of the use of this template tag to display a list of news:

.. code-block:: html+django

    <h2>Latest news</h2>
    {% get_page "news" as news_page %}
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
-------------------

This tag show the absolute url of a page. The difference with the `Page.get_url_path` method is
that the template knows which language is used within the context and display the URL accordingly:

.. code-block:: html+django

    {% show_absolute_url current_page %}

.. note::

    You can use either the page object, the slug, or the id of the page.


Delegate the page rendering to another application
----------------------------------------------------

:doc:`You can set another application to render certain pages of your website </3rd-party-apps>`.

Subclass the default view
-----------------------------

This CMS view is a class based view. This means is is easy
to override some default behavior. For example if you want to inject
additional context information into all the pages templates you can override
th method extra_context::


    from pages.views import Details
    from news.models import News

    class NewsView(Details):

        def extra_context(self, request, context):
            lastest_news = News.object.all()
            context.update({'news': lastest_news})

    details = NewsView()

For your view to be used in place of the CMS one, you simply need
to point to it with something similar to this::

    from django.conf.urls.defaults import url, include, patterns
    from YOUR_APP.views import details
    from pages import page_settings

    if page_settings.PAGE_USE_LANGUAGE_PREFIX:
        urlpatterns = patterns('',
            url(r'^(?P<lang>[-\w]+)/(?P<path>.*)$', details,
                name='pages-details-by-path')
        )
    else:
        urlpatterns = patterns('',
            url(r'^(?P<path>.*)$', details, name='pages-details-by-path')
        )

.. note::

    Have a look at `pages.urls` for a up to date example of URLs configuration.

