=========================
Placeholders template tag
=========================

The syntax for placeholder is the following::

    {% placeholder <name> [on <page>] [with <widget>] [parsed] [as <varname>] %}

A few explanations are needed:

* If the **on** option is omitted the CMS will automatically
  take the current page (by using the `current_page` context variable)
  to get the content of the placeholder.

* If the **widget** option is omitted the CMS will render a simple `TextInput`.

* If you use the keyword **parsed** the content of the placeholder
  will be evaluated as Django template, within the current context.

* Each placeholder with the **parsed** keyword defined will also have
  a note in the admin interface noting its ability to be evaluated as template.

* If you use the option **as** you will define in the template's context
  with the content of the placeholder that you will be able to use for different purpose.

To clarify, here is a list of different possible syntaxes for this template tag::

    {% placeholder title %}
    {% placeholder title with TextIntput %}
    {% placeholder body with Textarea %}
    {% placeholder right-column on another_page_object %}
    
    {% placeholder body parsed %}
    {% placeholder right-column as right_column %}

    ..random content..

    <div class="my_funky_column">{{ right_column|safe }}</div>


Image placeholder
=================

You can also use a special placeholder for images::

    {% imageplaceholder body-image as imgsrc %}
    {% if imgsrc %}
        <img src="{{ MEDIA_URL }}{{ imgsrc }}" alt=""/>
    {% endif %}

A file upload field will appears into the page admin interface.


Create your own placeholder
===========================

If you want to create yout own new type of placeholder,
you can simple subclass the :class:`PlaceholderNode <pages.placeholders.PlaceholderNode>`::

    from pages.placeholders import PlaceholderNode
    from pages.templatetags.page_tags import parse_placeholder
    register = template.Library()

    class ContactFormPlaceholderNode(PlaceholderNode):

        def __init__(self, name, *args, **kwargs):
            ...

        def get_widget(self, page, language, fallback=Textarea):
            """Redefine this to change the widget of the field."""
            ...

        def get_field(self, page, language, initial=None):
            """Redefine this to change the field displayed in the admin."""
            ...

        def save(self, page, language, data, change):
            """Redefine this to change the way to save the placeholder data."""
            ...

        def render(self, context):
            """Output the content of the node in the template."""
            ...

    def do_imageplaceholder(parser, token):
        name, params = parse_placeholder(parser, token)
        return ContactForm(name, **params)
    register.tag('contactplaceholder', do_imageplaceholder)

And use it your templates as a normal placeholder::

    {% contactplaceholder contact %}


Changing the widget of the common placeholder
=============================================

If you want to just redefine the widget of the default :class:`PlaceholderNode <pages.placeholders.PlaceholderNode>`
without subclassing it, you can just you create a valid Django Widget that take an extra language paramater::

    from django.forms import Textarea
    from django.utils.safestring import mark_safe

    class CustomTextarea(Textarea):
        class Media:
            js = ['path to the widget extra javascript']
            css = {
                'all': ['path to the widget extra javascript']
            }

        def __init__(self, language=None, attrs=None, **kwargs):
            attrs = {'class': 'custom-textarea'}
            super(CustomTextarea, self).__init__(attrs)

        def render(self, name, value, attrs=None):
            rendered = super(CustomTextarea, self).render(name, value, attrs)
            return mark_safe("""Take a look at \
                    example.widgets.CustomTextarea<br>""") \
                    + rendered

Create a file named widgets (or whathever you want) somewhere in one of your project's application
and then you can simply use the placeholder syntax.

If your widget is in the `example.widgets` module the syntax should look like this::

    {% placeholder custom_widget_example with example.widgets.CustomTextarea parsed  %}

More examples of custom widgets are available in :mod:`pages/admin/widgets.py <pages.admin.widgets>`.

List of placeholder widgets shipped with the CMS
================================================

Placeholder could be rendered with different widgets

TextInput
---------

A simple line input::

    {% placeholder [name] with TextInput %}

Textarea
--------

A multi line input::

    {% placeholder [name] with Textarea %}

RichTextarea
------------

A simple `Rich Text Area Editor <http://batiste.dosimple.ch/blog/posts/2007-09-11-1/rich-text-editor-jquery.html>`_ based on jQuery::

    {% placeholder [name] with RichTextarea %}

.. image:: http://rte-light.googlecode.com/svn/trunk/screenshot.png

WYMEditor
---------

A complete jQuery Rich Text Editor called `wymeditor <http://www.wymeditor.org/>`_::

    {% placeholder [name] with WYMEditor %}

.. image:: http://drupal.org/files/images/wymeditor.preview.jpg

markItUpMarkdown
----------------

markdown editor based on `markitup <http://markitup.jaysalvat.com/home/>`_::

    {% placeholder [name] with markItUpMarkdown %}

.. image:: http://www.webdesignerdepot.com/wp-content/uploads/2008/11/05_markitup.jpg

markItUpHTML
------------

A HTML editor based on `markitup <http://markitup.jaysalvat.com/home/>`_::

    {% placeholder [name] with markItUpHTML %}

.. image:: http://t37.net/files/markitup-081127.jpg

TinyMCE
-------

HTML editor based on `TinyMCE <http://tinymce.moxiecode.com/>`_

1. You should install the `django-tinymce <http://pypi.python.org/pypi/django-tinymce/1.5>`_ application first
2. Then in your settings you should activate the application::

    PAGE_TINYMCE = True

3. And add ``tinymce`` in your ``INSTALLED_APPS`` list.

The basic javascript files required to run TinyMCE are distributed with this CMS.

However if you want to use plugins you need to fully install TinyMCE.
To do that follow carefully `those install instructions <http://code.google.com/p/django-tinymce/source/browse/trunk/docs/installation.rst>`_

Usage::

    {% placeholder [name] with TinyMCE %}

.. image:: http://mgccl.com/gallery2/g2data/albums/2006/11/tinymce.png

EditArea
--------

Allows to edit raw html code with syntax highlight based on [http://www.cdolivet.com/index.php?page=editArea editArea]

The code (Javascript, CSS) for editarea is not included into the codebase.
To get the code you can add this into your svn external dependecies::

    pages/media/pages/edit_area -r29 https://editarea.svn.sourceforge.net/svnroot/editarea/trunk/edit_area

Usage::

    {% placeholder [name] with EditArea %}

.. image:: http://sourceforge.net/dbimage.php?id=69125&image.png


