==============================
List of all available settings
==============================

GERBI_TEMPLATES
==================================

GERBI_TEMPLATES is a list of tuples that specifies the which templates
are available in the ``gerbi`` admin.  Templates should be assigned in
the following format::

    GERBI_TEMPLATES = (
        ('gerbi/nice.html', 'nice one'),
        ('gerbi/cool.html', 'cool one'),
    )

One can also assign a callable (which should return the tuple) to this
setting to achieve dynamic template list e.g.::

    def _get_templates():
        # to avoid any import issues
        from app.models import PageTemplate
        return PageTemplate.get_page_templates()

    GERBI_TEMPLATES = _get_templates

Where the model might look like this::

    class PageTemplate(OrderedModel):
        name = models.CharField(unique=True, max_length=100)
        template = models.CharField(unique=True, max_length=260)

        @staticmethod
        def get_page_templates():
            return PageTemplate.objects.values_list('template', 'name')

        class Meta:
            ordering = ["order"]

        def __unicode__(self):
            return self.name


GERBI_DEFAULT_TEMPLATE
=============================

You *must* set ``GERBI_DEFAULT_TEMPLATE`` to the path of your default template::

    GERBI_DEFAULT_TEMPLATE = 'gerbi/index.html'


GERBI_LANGUAGES
==================================

A list tuples that defines the languages that pages can be translated into::

    gettext_noop = lambda s: s

    GERBI_LANGUAGES = (
        ('zh-cn', gettext_noop('Chinese Simplified')),
        ('fr-ch', gettext_noop('Swiss french')),
        ('en-us', gettext_noop('US English')),
    )


GERBI_DEFAULT_LANGUAGE
==================================

Defines which language should be used by default.  If
``GERBI_DEFAULT_LANGUAGE`` not specified, then project's
``settings.LANGUAGE_CODE`` is used::

    LANGUAGE_CODE = 'en-us'

GERBI_LANGUAGE_MAPPING
==================================

GERBI_LANGUAGE_MAPPING must be a function that takes
the language code of the incoming browser as an argument.

This function can change the incoming client language code to another language code,
presumably one for which you are managing trough the CMS.

This is useful if your project only has one set of translation strings
for a language like Chinese, which has several variants like ``zh-cn``, ``zh-tw``, ``zh-hk``,
but you don't have a translation for every variant.

`GERBI_LANGUAGE_MAPPING` help you to server the same Chinese translation to all those Chinese variants,
not just those with the exact ``zh-cn`` locale.

Enable that behavior here by assigning the following function to the
``GERBI_LANGUAGE_MAPPING`` variable::

    # here is all the languages supported by the CMS
    GERBI_LANGUAGES = (
        ('de', gettext_noop('German')),
        ('fr-fr', gettext_noop('Swiss french')),
        ('en-us', gettext_noop('US English')),
    )

    # copy GERBI_LANGUAGES
    languages = list(GERBI_LANGUAGES)

    # Other languages accepted as a valid client language
    languages.append(('fr-fr', gettext_noop('French')))
    languages.append(('fr-be', gettext_noop('Belgium french')))

    # redefine the LANGUAGES setting in order to be sure to have the correct request.LANGUAGE_CODE
    LANGUAGES = languages

    # Map every french based language to fr-fr
    def language_mapping(lang):
        if lang.startswith('fr'):
            return 'fr-fr'
        return lang
    GERBI_LANGUAGE_MAPPING = language_mapping

PAGES_MEDIA_URL
==================================

URL that handles gerbi.media. If not set the default value is::

    <STATIC_URL|MEDIA_URL>gerbi/

GERBI_UNIQUE_SLUG_REQUIRED
==================================

Set ``GERBI_UNIQUE_SLUG_REQUIRED`` to ``True`` to enforce unique slug names
for all pages.

GERBI_CONTENT_REVISION
==================================

Set ``GERBI_CONTENT_REVISION`` to ``False`` to disable the recording of
gerbi.revision information in the database

SITE_ID
==================================

Set SITE_ID to the id of the default ``Site`` instance to be used on
installations where content from a single installation is served on
multiple domains via the ``django.contrib.sites`` framework.

GERBI_USE_SITE_ID
==================================

Set GERBI_USE_SITE_ID to ``True`` to make use of the ``django.contrib.sites``
framework

GERBI_USE_LANGUAGE_PREFIX
==================================

Set GERBI_USE_LANGUAGE_PREFIX to ``True`` to make the ``get_absolute_url``
method to prefix the URLs with the language code

GERBI_CONTENT_REVISION_EXCLUDE_LIST
==========================================

Assign a list of placeholders to GERBI_CONTENT_REVISION_EXCLUDE_LIST
to exclude them from the revision process.

GERBI_SANITIZE_USER_INPUT
==================================

Set ``GERBI_SANITIZE_USER_INPUT`` to ``True`` to sanitize the user input with
``html5lib``.


GERBI_HIDE_ROOT_SLUG
==================================

Hide the slug's of the first root page ie: ``/home/`` becomes ``/``

GERBI_SHOW_START_DATE
==================================

Show the publication start date field in the admin.  Allows for future dating
Changing the ``GERBI_SHOW_START_DATE``  from ``True`` to ``False``
after adding data could cause some weirdness.  If you must do this, you
should update your database to correct any future dated pages.

GERBI_SHOW_END_DATE
==================================

Show the publication end date field in the admin, allows for page expiration
Changing ``GERBI_SHOW_END_DATE`` from ``True`` to ``False`` after adding
data could cause some weirdness.  If you must do this, you should update
your database and null any pages with ``publication_end_date`` set.

GERBI_CONNECTED_MODELS
==================================

``GERBI_CONNECTED_MODELS`` allows you to specify a model and form for this
model into your settings to get an automatic form to create
and directly link a new instance of this model with your page in the admin::

    GERBI_CONNECTED_MODELS = [
        {'model':'documents.models.Document',
            'form':'documents.models.DocumentForm'},
    ]

.. note::

    :ref:`Complete documentation on how to use this setting <3rd-party-apps>`


GERBI_TAGGING
==================================

Set ``GERBI_TAGGING`` to ``False`` if you do not wish to use the
``django-taggit`` application.

GERBI_TINYMCE
==================================

Set this to ``True`` if you wish to use the ``django-tinymce`` application.

GERBI_EXTRA_CONTEXT
==================================

This setting is a function that can be defined if you need to pass extra
context data to the pages templates.
