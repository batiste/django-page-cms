"""Django page CMS urls module."""

from django.conf.urls import re_path
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
            re_path(r'^api/$', api.PageList.as_view()),
            re_path(r'^api/pages/$', api.PageList.as_view()),
            re_path(r'^api/pages/(?P<pk>[0-9]+)/$', api.PageEdit.as_view()),
            re_path(r'^api/contents/$', api.ContentList.as_view()),
            re_path(r'^api/contents/(?P<pk>[0-9]+)/$', api.ContentEdit.as_view())
        ]

if settings.PAGE_USE_LANGUAGE_PREFIX:
    urlpatterns += [
        re_path(r'^(?P<lang>[-\w]+)/(?P<path>.*)$', views.details,
            name='pages-details-by-path'),
        re_path(r'^$', views.details, {'path': '', 'name': 'pages-root'}),
    ]
else:
    urlpatterns += [
        re_path(r'^(?P<path>.*)$', views.details, name='pages-details-by-path'),
        re_path(r'^$', views.details, {'path': '', 'name': 'pages-root'}),
    ]
