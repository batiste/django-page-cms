======================
3th party applications
======================

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

 