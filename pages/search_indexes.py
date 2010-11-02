"""Django haystack `SearchIndex` module."""
from pages.models import Page

from haystack.indexes import SearchIndex, CharField, DateTimeField
from haystack import site


class PageIndex(SearchIndex):
    """Search index for pages content."""
    text = CharField(document=True, use_template=True)
    title = CharField(model_attr='title')
    url = CharField(model_attr='get_absolute_url')
    publication_date = DateTimeField(model_attr='publication_date')

    def get_queryset(self):
        """Used when the entire index for model is updated."""
        return Page.objects.published()

site.register(Page, PageIndex)
