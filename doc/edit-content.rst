===================================
Inline page editing
===================================

Gerbi CMS provide a way to easily edit the placeholder's content
on your own frontend when you are authenticated as a staff user.

.. image:: images/inline-edit.png

To activate the feature on your frontend you need to add 2 tags inside your templates. One in your <head> tag and one in the <body> tag:

.. code-block:: html+django

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

For placeholder editing to work properly you will need to surround the placeholder with an HTML element like so:

.. code-block:: html+django

    <div>
        {% placeholder "title" %}
    </div>

Placeholder editing works automatically by injecting an HTML comment into the placeholder output. So thing
like this will not work:

.. code-block:: html+django

    <div>
        <img src="{{ MEDIA_URL }}{% imageplaceholder "img" %}">
    </div>

Because the rendered comment will not result into an HTML node:

.. code-block:: html+django

    <div>
        <img src="upload/image.png<!--placeholder:img-->">
    </div>

To fix this issue you can use placeholders as rendering blocks like so:

.. code-block:: html+django

    <div>
        {% imageplaceholder 'img' block %}
            {% if content %}
                <img src="{{ MEDIA_URL }}{{ content }}" class="img-responsive" alt="">
            {% endif %}
        {% endplaceholder %}
    </div>
