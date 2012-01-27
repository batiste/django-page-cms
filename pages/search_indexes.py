"""Django haystack `SearchIndex` module."""
from pages.models import Page
from pages import settings

from haystack.indexes import SearchIndex, CharField, DateTimeField, RealTimeSearchIndex
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


class RealTimePageIndex(RealTimeSearchIndex):
    """Search index for pages content."""
    text = CharField(document=True, use_template=True)
    title = CharField(model_attr='title')
    url = CharField(model_attr='get_absolute_url')
    publication_date = DateTimeField(model_attr='publication_date')

    def get_queryset(self):
        """Used when the entire index for model is updated."""
        return Page.objects.published()

if settings.PAGE_REAL_TIME_SEARCH:
    site.register(Page, RealTimePageIndex)
else:
    site.register(Page, PageIndex)

