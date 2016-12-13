===================================
Inline page editing
===================================

Gerbi CMS provide a way to easily edit the placeholder's content
on your own frontend when you are authenticated as a staff user.

.. image:: images/inline-edit.png

To activate the feature on your frontend you need to add 2 tags inside your templates. One in your <head> tag and one in the <body> tag::

    <html>
        <head>
            ...
            {% pages_edit_media %}
        </head>
        <body>
            ...
            {% pages_edit_init %}
        </body>
    </html>

For placeholder editing to work properly you will need to surround the placeholder with an HTML element like so::

    <div>
        {% placeholder "title" %}
    </div>

Placeholder editing works automatically by injecting an HTML comment into the placeholder output. So thing
like this will not work::

    <div>
        <img src="{{ MEDIA_URL }}{% imageplaceholder "img" %}">
    </div>

Because the rendered comment will not result into an HTML node::

    <div>
        <img src="upload/image.png<!--placeholder:img-->">
    </div>

This will not only not work but will also break the image source in edit mode. Here
is an imperfect way to fix this problem::

    {% if request.user.is_staff %}
        <button>Change image: {% imageplaceholder 'header-image' %}</button>
    {% endif %}
    {% page_has_content 'header-image' current_page %}
        {% imageplaceholder 'header-image' as image %}
        <img src="{{ MEDIA_URL }}{{ image }}">
    {% end_page_has_content %}

When the as option is used the special HTML comment is not generated therefore not breaking the source of the image. The solution is not perfect because the image source doesn't get updated automatically.