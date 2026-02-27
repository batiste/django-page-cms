from django.conf.urls import patterns, url, include

urlpatterns = patterns('',
    url(r'^import-json/$',
        'pages.plugins.jsonexport.actions.import_pages_from_json', 
        name='import-pages-from-json'),
)