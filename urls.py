from django.conf.urls.defaults import *
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^cms/', include('cms.foo.urls')),
    (r'^pages/$', 'pages.views.details'),
    (r'^pages/.*?(?P<page_id>[0-9]+)/$', 'pages.views.details'),
    
    # Uncomment this for admin:
    #(r'^admin/pages/page/$', 'pages.admin_views.list_page'),
    (r'^admin/pages/page/$', 'pages.admin_views.list_pages'),
    (r'^admin/pages/page/(?P<page_id>\d+)/traduction/(?P<language_id>\w+)/$', 'pages.admin_views.traduction'),
    (r'^admin/pages/page/(?P<page_id>\d+)/$', 'pages.admin_views.modify'),
    (r'^admin/pages/page/add/$', 'pages.admin_views.add'),
    
    (r'^admin/(.*)', admin.site.root),
)
