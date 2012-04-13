"""Django page CMS urls module."""

from django.conf.urls.defaults import url, include, patterns
from django.conf.urls.defaults import handler404, handler500
from pages.views import details
from pages import settings

if settings.PAGE_USE_LANGUAGE_PREFIX:
    urlpatterns = patterns('',
        url(r'^(?P<lang>[-\w]+)/(?P<path>.*)$', details,
            name='pages-details-by-path'),
        # can be used to change the URL of the root page
        #url(r'^$', details, name='pages-root'),
    )
else:
    urlpatterns = patterns('',
        url(r'^(?P<path>.*)$', details, name='pages-details-by-path'),
        # can be used to change the URL of the root page
        #url(r'^$', details, name='pages-root'),
    )
