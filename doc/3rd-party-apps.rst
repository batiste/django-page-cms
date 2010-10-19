==========================
 Third party applications
==========================


Delegate the rendering of a page to an application
===================================================

By delegating the rendering of a page to another application, you will
be able to use customized views and still get all the CMS variables
to render a proper navigation.

First you need a `urls.py` file that you can register to the CMS. It might look like this::

    from django.conf.urls.defaults import *
    from pages.testproj.documents.views import document_view
    from pages.http import pages_view

    urlpatterns = patterns('',
        url(r'doc-(?P<document_id>[0-9]+)$', pages_view(document_view), name='document_details'),
        url(r'$', pages_view(document_view), name='document_root'),
    )

.. note::

    The decorator `pages_view` is important. This decorator will ensure
    that the CMS default view will be called before yours to get the context
    variables.

Then you need to register the urlconf module of your application to use it
within the admin interface. Here is an example for a document application::

    from pages.urlconf_registry import register_urlconf

    register_urlconf('Documents', 'pages.testproj.documents.urls',
        label='Display documents')

As soon as you have registered your `urls.py`, a new field will appear in the page administration.
Choose the `Display documents`. The view used to render this page on the frontend
is now choosen by `pages.testproj.documents.urls`.

.. note::

    The path passed to your urlconf module is the remaining path
    available after the page slug. Eg: `/pages/page1/doc-1` will become `doc-1`.

Here is an example of a valid view from the documents application::

    from django.shortcuts import render_to_response
    from django.template import RequestContext
    from pages.testproj.documents.models import Document

    def document_view(request, *args, **kwargs):
        context = RequestContext(request, kwargs)
        if kwargs.get('current_page', False):
            documents = Document.objects.filter(page=kwargs['current_page'])
            context['documents'] = documents
        if kwargs.has_key('document_id'):
            document = Document.objects.get(pk=int(kwargs['document_id']))
            context['document'] = document
        context['in_document_view'] = True
        return render_to_response('pages/examples/index.html', context)

The `document_view` will receive a bunch of extra parameters related to the CMS:

    * `current_page` the page object,
    * `path` the path used to reach the page,
    * `lang` the current language,
    * `pages_navigation` the list of pages used to render navigation.

.. note::

    If the field doesn't appear within the admin interface make sure that
    your registry code is executed properly.

.. note::

    Look at the testproj in the repository for an example on how to integrate
    an external application.

.. _3rd-party-apps:

Integrate application models and forms into the page admin
==========================================================

Django page CMS provide a solid way to integrate external application
forms for managing page related objects (create/delete/update) into the page's administration interface.

For this you need an object with foreign key pointing to a page::

    class Document(models.Model):
        "A dummy model used to illustrate the use of linked models in django-page-cms"

        title = models.CharField(_('title'), max_length=100, blank=False)
        text = models.TextField(_('text'), blank=True)

        # the foreign key *must* be called page
        page = models.ForeignKey(Page)

    class DocumentForm(ModelForm):
        class Meta:
            model = Document

After that you need to set up the PAGE_CONNECTED_MODELS into your settings similar to this one::

    PAGE_CONNECTED_MODELS = [{
        'model':'documents.models.Document',
        'form':'documents.models.DocumentForm',
        'options':{
                'extra': 3,
                'max_num': 10,
            },
    },]

When you edit a page, you should see a form to create/update/delete a Document object linked to this page.

