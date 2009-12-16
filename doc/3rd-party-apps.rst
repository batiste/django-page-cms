======================
3th party applications
======================

Delegate the rendering of a page to an application
===================================================

If you want to use another Django application but still have this application
represented into the CMS navigation you can delegate the page rendering to any
kind of view::

    from django.shortcuts import render_to_response
    from django.template import loader, Context, RequestContext

    def blog(request, **kwargs):
        context = RequestContext(request, kwargs)
        return render_to_response('pages/index.html', context)

The view will receive a bunch of extra parameters related to the CMS:

    * `current_page` the page object,
    * `path` the path used to reach the page,
    * `lang` the current language,
    * `pages_navigation` the list of pages used to render navigation.

Then you need to register this view to be able to use it within the admin interface::

    from example.views import blog
    from pages.views_registry import register_view
    register_view('Blog', blog, label='Blog of the company')

As soon as you registerd your view, a new field will appear in the page edition.

.. note::

    If the field doesn't appear within the admin interface make sure that
    the regsitry code is executed at some point in time.

Integrate application models and forms into the page admin
==========================================================

Django page CMS provide a solid way to integrate external application
forms for managing page related objects (create/delete/update) into the page's administraion interface.

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

 