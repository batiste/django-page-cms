=========================
Placeholders template tag
=========================

.. contents::

The placeholder template tag is what make Django Page CMS special. The workflow
is that you design your template first according to the page design.
Then you put placeholder tag where you want dynamic content.

For each placeholder you will have a corresponding field appearing automaticaly
in the administration interface. You can make as many templates as you want, even
use the template inheritance: this CMS administration will still behave as intended.

The syntax for a placeholder tag is the following::

    {% placeholder <name> [on <page>] [with <widget>] [parsed] [inherited] [as <varname>] %}

Detailed explanations on placeholder options
============================================

the **on** option
------------------

If the **on** option is omitted the CMS will automatically
take the current page (by using the `current_page` context variable)
to get the content of the placeholder. 

Template syntax example::

    {% placeholder main_menu on root_page %}

the **widget** option
----------------------

If the **widget** option is used to change the way the CMS administration interface.

By default the CMS will use a simple `TextInput` widget. Otherwise the CMS will use the
widget fo your choice. Widgets need to be registered before you can use them in the CMS::

    from pages.widgets_registry import register_widget
    from django.forms import TextInput

    class NewWidget(TextInput):
        pass
    
    register_widget(NewWidget)

Template syntax example::

    {% placeholder body with NewWidget %}


.. note::

    This CMS is shipped with :ref:`a list of useful widgets <placeholder-widgets-list>` .

The **as** option
------------------

If you use the option **as** the content of the placeholder content will not be displayed:
a variable of your choice will be defined within the template's context.

Template syntax example::

    {% placeholder image as image_src %}
    <img src="{{ img_src }}" alt=""/>

The **parsed** keyword
-----------------------

If you add the keyword **parsed** the content of the placeholder
will be evaluated as Django template, within the current context.
Each placeholder with the **parsed** keyword will also have
a note in the admin interface noting its ability to be evaluated as template.

Template syntax example::

    {% placeholder special-content parsed %}

The **inherited** keyword
-------------------------

If you add the keyword **inherited** the placeholder's content displayed
on the frontend will be retrieved from the closest parent. But only if there is no
content for the current page.

Template syntax example::

    {% placeholder right-column inherited %}

The **untranslated** keyword
-----------------------------

If you add the keyword **untranslated** the placeholder's content
will be the same whatever language your use. It's especialy useful for an image
placeholder that should remain the same in every language.

Template syntax example::

    {% placeholder logo untranslated %}

Examples of other valid syntaxes
------------------------------------

This is a list of different possible syntaxes for this template tag::

    {% placeholder title with TextIntput %}
    {% placeholder logo untranslated on root_page %}
    {% placeholder right-column inherited as right_column parsed %}

    ...
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

If you want to create your own new type of placeholder,
you can simply subclass the :class:`PlaceholderNode <pages.placeholders.PlaceholderNode>`::

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

    def do_contactplaceholder(parser, token):
        name, params = parse_placeholder(parser, token)
        return ContactFormPlaceholderNode(name, **params)
    register.tag('contactplaceholder', do_contactplaceholder)

And use it your templates as a normal placeholder in your templates::

    {% contactplaceholder contact %}


Changing the widget of the common placeholder
=============================================

If you want to just redefine the widget of the default :class:`PlaceholderNode <pages.placeholders.PlaceholderNode>`
without subclassing it, you can just you create a valid Django Widget that take an extra language paramater::

    from django.forms import Textarea
    from django.utils.safestring import mark_safe
    from pages.widgets_registry import register_widget

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

    register_widget(CustomTextarea)

Create a file named widgets (or whathever you want) somewhere in one of your project's application
and then you can simply use the placeholder syntax::

    {% placeholder custom_widget_example CustomTextarea parsed  %}

More examples of custom widgets are available in :mod:`pages.widgets.py <pages.widgets>`.

.. _placeholder-widgets-list:

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

AdminTextInput
--------------

A simple line input with Django admin CSS styling (better for larger input fields)::

    {% placeholder [name] with AdminTextInput %}

AdminTextarea
-------------

A multi line input with Django admin CSS styling::

    {% placeholder [name] with AdminTextarea %}

FileBrowseInput
---------------

A file browsing widget::

    {% placeholder [name] with FileBrowseInput %}

.. note::

    The following django application needs to be installed: http://code.google.com/p/django-filebrowser/


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

CKEditor
---------

A complete JavaScript Rich Text Editor called `CKEditor <http://ckeditor.com/>`_::

    {% placeholder [name] with CKEditor %}

.. image:: http://drupal.org/files/images/ckeditor_screenshot.png

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

AutoCompleteTagInput
---------------------

Provide a dynamic auto complete widget for tags used on pages::

    {% placeholder [name] with AutoCompleteTagInput %}


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

Allows to edit raw html code with syntax highlight based on this project: http://www.cdolivet.com/index.php?page=editArea

Basic code (Javascript, CSS) for editarea is included into the codebase.
If you want the full version you can get it there::

    pages/media/pages/edit_area -r29 https://editarea.svn.sourceforge.net/svnroot/editarea/trunk/edit_area

Usage::

    {% placeholder [name] with EditArea %}

.. image:: http://sourceforge.net/dbimage.php?id=69125&image.png


