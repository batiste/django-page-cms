"""Django haystack `SearchIndex` module."""
from pages.models import Page
from pages import settings

from haystack.indexes import SearchIndex, CharField, DateTimeField, RealTimeSearchIndex

if settings.PAGE_REAL_TIME_SEARCH:
    class RealTimePageIndex(RealTimeSearchIndex):
        """Search index for pages content."""
        text = CharField(document=True, use_template=True)
        title = CharField(model_attr='title')
        url = CharField(model_attr='get_absolute_url')
        publication_date = DateTimeField(model_attr='publication_date')

        def get_queryset(self):
            """Used when the entire index for model is updated."""
            return Page.objects.published()

        def get_model(self):
            Page

        def should_update(self, instance, **kwargs):
            return instance.status == Page.PUBLISHED

else:
    class PageIndex(SearchIndex):
        """Search index for pages content."""
        text = CharField(document=True, use_template=True)
        title = CharField(model_attr='title')
        url = CharField(model_attr='get_absolute_url')
        publication_date = DateTimeField(model_attr='publication_date')

        def get_queryset(self):
            """Used when the entire index for model is updated."""
            return Page.objects.published()

        def get_model(self):
            Page

        def should_update(self, instance, **kwargs):
            return instance.status == Page.PUBLISHED
