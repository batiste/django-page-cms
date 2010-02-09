"""Django haystack `SearchIndex` module."""
from pages.models import Page, Content

from haystack.indexes import SearchIndex, CharField, DateTimeField
from haystack import site

import datetime

class PageIndex(SearchIndex):
    """Search index for pages content."""
    text = CharField(document=True, use_template=True)
    publication_date = DateTimeField(model_attr='publication_date')

    def get_queryset(self):
        """Used when the entire index for model is updated."""
        return Page.objects.published()


site.register(Page, PageIndex)