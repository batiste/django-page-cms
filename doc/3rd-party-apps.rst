==========================
 Third party applications
==========================


Delegate the rendering of a page to an application
===================================================

By delegating the rendering of a page to another application, you will
be able to use customized views and still get all the CMS variables
to render a proper navigation.

First you need to register the urlconf module of your application to use it
within the admin interface. Here is an example for a document application::

    from pages.urlconf_registry import register_urlconf

    register_urlconf('Documents', 'example.documents.urls',
        label='Display documents')

As soon as you have registered your urlconf, a new field will appear in the page administration.
Choose the `Display documents`. The view used to render this page on the frontend
is now choosen by `example.documents.urls`.

This is a valid example from the documents application::

    from django.shortcuts import render_to_response
    from django.template import loader, Context, RequestContext
    from example.documents.models import Document

    def document_view(request, **kwargs):
        context = RequestContext(request, kwargs)
        documents = Document.objects.filter(page=kwargs['current_page'])
        context['documents'] = documents
        if kwargs.has_key('document_id'):
            document = Document.objects.get(pk=int(kwargs['document_id']))
            context['document'] = document
        context['in_document_view'] = True
        return render_to_response('pages/index.html', context)

The `document_view` will receive a bunch of extra parameters related to the CMS:

    * `current_page` the page object,
    * `path` the path used to reach the page,
    * `lang` the current language,
    * `pages_navigation` the list of pages used to render navigation.

.. note::

    If the field doesn't appear within the admin interface make sure that
    your registry code is executed properly.

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

 