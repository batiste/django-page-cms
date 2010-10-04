===================================
Display page's content in templates
===================================

Django page CMS provide several template tags to extract data from the CMS.
To use these tags in your templates you must load them first::

    {% load pages_tags %}

.. contents::
    :local:
    :depth: 2

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


Display content from other applications
----------------------------------------

There is several ways to change the way the default view provided
by the CMS render the pages. This list try explain the most common.

Using the PAGE_EXTRA_CONTEXT setting
======================================

Considering you have a simple news model::

    class News(models.Model):
        title = models.CharField(max_length=200)
        postdate = models.DateTimeField(default=datetime.now)
        body = models.CharField(max_length=200)

And that you would like to display a list of news into some of your page's templates::

    <ul>
    {% for new in news %}
        <li>
            <h2>{{ news.title }}</p>
            <p>{{ news.body }}</p>
        </li>
    {% endfor %}
    </ul>

Then you might want to use the `PAGE_EXTRA_CONTEXT` setting. You should set this setting to be a function.
This function should return a Python dictionary. This dictionary will be merged with the context of
every page of your website.

Example in the case of the news::

    def extra_context():
        from news.models import News
        lastest_news = News.object.all()
        return {'news': lastest_news}

    PAGE_EXTRA_CONTEXT = extra_context

Delegate the page rendering to another application
===================================================

:doc:`You can set another application to render certain pages of your website </3rd-party-apps>`.

Subclass the default view
===================================================

New in 1.2.3: The default view is now a real class. That will
help if you want to override some default behavior::


    from pages.views import Details
    from news.models import News

    class NewsView(Details):

        def extra_context(self, request, context):
            lastest_news = News.object.all()
            return {'news': lastest_news}
