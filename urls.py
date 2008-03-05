from django.conf.urls.defaults import *

urlpatterns = patterns('',
    # Example:
    # (r'^cms/', include('cms.foo.urls')),
    (r'^pages/$', 'pages.views.details'),
    (r'^pages/.*(?P<page_id>[0-9]+)/$', 'pages.views.details'),
    
    # Uncomment this for admin:
    #(r'^admin/pages/page/$', 'pages.admin_views.list_page'),
    (r'^admin/hierarchical/hierarchicalnode/$', 'hierarchical.admin_views.list_nodes'),
    #(r'^admin/hierarchical/hierarchicalnode/add/$', 'hierarchical.admin_views.add'),
    #(r'^admin/pages/hierarchicalnode/(?P<node_id>\d+)/$', 'pages.admin_views.modify'),
    (r'^admin/hierarchical/hierarchicalnode/(?P<hnode_id>\d+)/up/$', 'hierarchical.admin_views.up'),
    (r'^admin/hierarchical/hierarchicalnode/(?P<hnode_id>\d+)/down/$', 'hierarchical.admin_views.down'),
    (r'^admin/hierarchical/hierarchicalobject/(?P<hobject_id>\d+)/$', 'hierarchical.admin_views.modify'),
    (r'^admin/hierarchical/hierarchicalobject/add/$', 'hierarchical.admin_views.add'),
    (r'^admin/hierarchical/objects_by_model/(?P<content_type_id>\d+)/$', 'hierarchical.admin_views.get_objects_by_model'),
    
    (r'^admin/pages/page/(?P<page_id>\d+)/traduction/(?P<language_id>\w+)/$', 'pages.admin_views.traduction'),
    (r'^admin/pages/page/(?P<page_id>\d+)/$', 'pages.admin_views.modify'),
    (r'^admin/pages/page/add/$', 'pages.admin_views.add'),
                
    (r'^admin/', include('django.contrib.admin.urls')),
)
