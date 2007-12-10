from django.conf.urls.defaults import *

urlpatterns = patterns('',
    # Example:
    # (r'^cms/', include('cms.foo.urls')),
    (r'^pages/$', 'pages.views.slug'),
    (r'^pages/(?P<slug>[^/]+)/$', 'pages.views.slug'),
    (r'^pages/.*/(?P<slug>[^/]+)/$', 'pages.views.slug'),
    
    # Uncomment this for admin:
    (r'^admin/pages/page/$', 'pages.admin_views.list_page'),
    (r'^admin/pages/page/add/$', 'pages.admin_views.add'),
    (r'^admin/pages/page/(?P<page_id>\d+)/$', 'pages.admin_views.modify'),
    (r'^admin/pages/page/(?P<page_id>\d+)/up/$', 'pages.admin_views.up'),
    (r'^admin/pages/page/(?P<page_id>\d+)/down/$', 'pages.admin_views.down'),
    (r'^admin/pages/page/(?P<page_id>\d+)/traduction/(?P<language_id>\w+)/$', 'pages.admin_views.traduction'),
    (r'^admin/', include('django.contrib.admin.urls')),
)
