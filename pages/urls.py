"""Django page CMS urls module."""

from django.conf.urls import url, include, patterns
from django.conf.urls import handler404, handler500
from pages import views
from pages import settings

urlpatterns = patterns('',
    url(r'^api/$', views.api_list),
    url(r'^api/(?P<pk>[0-9]+)/$', views.api_details)
)

if settings.PAGE_USE_LANGUAGE_PREFIX:
    urlpatterns += patterns('',
        url(r'^(?P<lang>[-\w]+)/(?P<path>.*)$', views.details,
            name='pages-details-by-path'),
        # can be used to change the URL of the root page
        #url(r'^$', details, name='pages-root'),
    )
else:
    urlpatterns += patterns('',
        url(r'^(?P<path>.*)$', views.details, name='pages-details-by-path'),
        # can be used to change the URL of the root page
        #url(r'^$', details, name='pages-root'),
    )
