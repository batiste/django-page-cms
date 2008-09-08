from django.conf.urls.defaults import *
from django.contrib import admin
import settings
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
    (r'^admin/pages/page/(?P<page_id>\d+)/valid-targets-list/$', 'pages.admin_views.valid_targets_list'),
    (r'^admin/pages/page/(?P<page_id>\d+)/move_page/$', 'pages.admin_views.move_page'),
    (r'^admin/(.*)', admin.site.root),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        # Trick for Django to support static files (security hole: only for Dev environement! remove this on Prod!!!)
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
        url(r'^admin_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.ADMIN_MEDIA_ROOT}),
    )
