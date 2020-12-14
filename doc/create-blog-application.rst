================================
How to create a Blog application
================================

A Blog is made of dated Blog Posts. It so happens this CMS pages model
contain a creation date and is flexible enough to contain all sort contents that could
be useful in a Blog post.
So how can we use this CMS to create a Blog application? This guide gives a step
by step recipe that demonstrate how easily you can build new features on 
top of this CMS.

Step 1: Create a new Django app within your project
------------------------------------------------------

.. code-block:: bash

  python manage.py startapp blog


Step 2: Create the views
---------------------------

Open you newly created `blog/views.py` file and create 2 views. One for the 
category view and another for the Blog's index.
We are using the `taggit` to handle the categories, this way a Blog can be in 
several categories.

.. code-block:: python

    from django.shortcuts import render
    from pages.models import Page
    from taggit.models import Tag
    from django.core.paginator import Paginator

    def category_view(request, *args, **kwargs):
        context = dict(kwargs)
        category = Tag.objects.get(id=kwargs['tag_id'])
        page = context['current_page']
        blogs = page.get_children_for_frontend().filter(tags__name__in=[category.name])

        paginator = Paginator(blogs, 8)
        page_index = request.GET.get('page')
        blogs = paginator.get_page(page_index)
        context['blogs'] = blogs
        
        context['category'] = category.name
        return render(request, 'blog-home.html', context)

    def blog_index(request, *args, **kwargs):
        context = dict(kwargs)
        page = context['current_page']
        blogs = page.get_children_for_frontend()

        paginator = Paginator(blogs, 7)
        page = request.GET.get('page')
        blogs = paginator.get_page(page)
        context['blogs'] = blogs
        context['template_name'] = 'blog-home.html'

        return render(request, 'blog-home.html', context)


Step 2: Link the views with the CMS
------------------------------------

Populate `blog/urls.py` with those urls

.. code-block:: python

    from django.conf.urls import url
    from blog import views
    from django.urls import include, path, re_path

    urlpatterns = [
      url(r'^category/(?P<tag_id>[0-9]+)$', views.category_view, name='blog_category_view'),
      url(r'^$', views.blog_index, name='blog_index')
    ]

Then the last step is to register this URL module with the CMS. Place this
code at the top of you project `urls.py` file.

.. code-block:: python

    from pages.urlconf_registry import register_urlconf
    register_urlconf('blog', 'blog.urls', label='Blog index')


Step 3: Create the blog templates
------------------------------------

You will need create 3 templates for your blog application. The first one is a helper template called `blog-card.html`.
It contains a basic representation of a blog as a card:

.. code-block:: html+django

    {% load pages_tags static i18n humanize thumbnail %}
    <div class="card mb-4 shadow-sm">
      <a class="blog-lead-image" href="{% show_absolute_url page %}">
        {% get_content page "lead-image" as image %}
        {% if image %}
          {% thumbnail image "320x240" crop="center" as img %}
            <img src="{{ img.url }}">
          {% endthumbnail %}
        {% else %}
          <!-- no image for this post -->
        {% endif %}
      </a>
      <div class="card-body">
        <a href="{% show_absolute_url page %}">
          <h3 class="my-0 font-weight-normal">{% show_content page "title" %}</h3>
        </a>
        <p>{% show_content page "lead" %}</p>
        {% if forloop.first %}
          {% get_content page "content" as content %}
          <p class="d-none d-lg-block">{{ content | striptags | safe | truncatechars:220 }}</p>
        {% endif %}
        <p class="blog-meta">Published {{ page.creation_date | naturalday }}
          {% if page.tags.count %}
            in the categories: 
            {% for tag in page.tags.all %}
              <a href="/{{ lang }}/blog/category/{{ tag.id }}">{{ tag.name }}</a>{% if not forloop.last %},{% endif %}
            {% endfor %}
          {% endif %}
          by {{ page.author.first_name }} {{ page.author.last_name }}
        </p>
      </div>
    </div>

The second is the `blog-home.html` referenced by the views you previoulsy wrote, it will be used by the index and
the categories:

.. code-block:: html+django

    {% extends 'index.html' %}
    {% load pages_tags static i18n humanize thumbnail %}

    {% block header %}
    <div class="px-3 py-3 pt-md-5 pb-md-4 mx-auto text-center">
      <h1 class="display-4">{% placeholder "title" %} {{ category }}</h1>
      <p class="lead">{% placeholder "lead" with Textarea %}</p>
    </div>
    {% endblock %}

    {% block content %}
      <div class="card-deck mb-3 text-center blog-home">
      {% for page in blogs %}
        {% include "blog-card.html" %}
      {% endfor %}
      </div>

      <div class="pagination">
          <span class="step-links">
              {% if blogs.has_previous %}
                  <a href="?page=1" class="btn btn-light">&laquo; first</a>
                  <a href="?page={{ blogs.previous_page_number }}" class="btn btn-light">previous</a>
              {% endif %}
      
              <span class="current">
                  Page {{ blogs.number }} of {{ blogs.paginator.num_pages }}.
              </span>
      
              {% if blogs.has_next %}
                  <a href="?page={{ blogs.next_page_number }}" class="btn btn-light">next</a>
                  <a href="?page={{ blogs.paginator.num_pages }}" class="btn btn-light">last &raquo;</a>
              {% endif %}
          </span>
      </div>
      {% endblock %}

Finaly the last one is for the Blog Post itself. You could have different Blog Post templates
but for now we only need one, let's call it `blog-post.html`:

.. code-block:: html+django

    {% extends 'index.html' %}
    {% load pages_tags static i18n humanize %}

    {% block header %}
    <div class="px-3 py-3 pt-md-5 pb-md-4 mx-auto text-center blog-post">
      <h1 class="display-4">{% placeholder "title" %}</h1>
      <p class="lead">{% placeholder "lead" with Textarea %}</p>
      <p class="blog-meta">Published {{ current_page.creation_date | naturalday }}
          {% if current_page.tags.count %}
            in the categories: 
            {% for tag in current_page.tags.all %}
              <a href="/{{ lang }}/blog/category/{{ tag.id }}">{{ tag.name }}</a>{% if not forloop.last %},{% endif %}
            {% endfor %}
          {% endif %}
          by {{ current_page.author.first_name }} {{ current_page.author.last_name }}
        </p>
    </div>
    {% endblock %}

    {% block content %}
    <div class="blog-post">
      <div class="blog-lead-image">
        {% imageplaceholder 'lead-image' block %}
          {% if content %}
            <img src="{{ MEDIA_URL }}{{ content }}" alt="">
          {% endif %}
        {% endplaceholder %}
      </div>

      <div>
        {% placeholder "content" with RichTextarea %}
      </div>
    </div>
    {% endblock %}

To finish things up you need to allow those 2 templates to be selected 
by the CMS. Add them to your `PAGE_TEMPLATES` setting:

.. code-block:: python

    PAGE_TEMPLATES = (
        ('index.html', 'Default template'),
        ('blog-post.html', 'Blog post'),
        ('blog-home.html', 'Blog home'),
    )


Step 4: Activate the Blog in the admin
------------------------------------------

You can now activate the Blog in the CMS admin. To do so follow those few steps:

1. Create a new page named "Blog", chose the template "Blog Home", and the option "Delegate to application: Blog Index".
2. Add a couple of child pages to this Blog Index page and chose the "Blog Post" template as their template.

The result should be a functional blog with an index page, category pages, tagging and pagination.

You are also free to create serveral Blog instances withing the CMS by repeating a version of this step. There is no restrictions.

`A fully functionnal version of this Blog application is available <https://github.com/batiste/django-page-cms/tree/master/example>`_ 
