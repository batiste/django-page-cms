from django.conf.urls.defaults import *
from django.contrib import admin
import settings
admin.autodiscover()

urlpatterns = patterns('',
    # Admin urls
    (r'^$', 'pages.admin_views.list_pages'),
    (r'^(?P<page_id>\d+)/traduction/(?P<language_id>\w+)/$', 'pages.admin_views.traduction'),
    (r'^(?P<page_id>\d+)/content/(?P<content_id>\w+)/$', 'pages.admin_views.content'),
    (r'^(?P<page_id>\d+)/$', 'pages.admin_views.modify'),
    (r'^add/$', 'pages.admin_views.add'),
    (r'^(?P<page_id>\d+)/valid-targets-list/$', 'pages.admin_views.valid_targets_list'),
    (r'^(?P<page_id>\d+)/move-page/$', 'pages.admin_views.move_page'),
    (r'^(?P<page_id>\d+)/change-status/$', 'pages.admin_views.change_status'),
)