"""Django page CMS urls module."""

from django.conf.urls import url
from pages import views
from pages import settings

urlpatterns = []

if settings.PAGE_API_ENABLED:
    try:
        from pages import api
    except ImportError as detail:
        print("API not present because of import error: %s" % detail)
    else:
        urlpatterns += [
            url(r'^api/$', api.PageList.as_view()),
            url(r'^api/pages/$', api.PageList.as_view()),
            url(r'^api/pages/(?P<pk>[0-9]+)/$', api.PageEdit.as_view()),
            url(r'^api/contents/$', api.ContentList.as_view()),
            url(r'^api/contents/(?P<pk>[0-9]+)/$', api.ContentEdit.as_view())
        ]

if settings.PAGE_USE_LANGUAGE_PREFIX:
    urlpatterns += [
        url(r'^(?P<lang>[-\w]+)/(?P<path>.*)$', views.details,
            name='pages-details-by-path'),
        # can be used to change the URL of the root page
        # url(r'^$', details, name='pages-root'),
    ]
else:
    urlpatterns += [
        url(r'^(?P<path>.*)$', views.details, name='pages-details-by-path'),
        # can be used to change the URL of the root page
        # url(r'^$', details, name='pages-root'),
    ]
