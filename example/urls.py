from django.conf.urls.defaults import url, include, patterns
from django.conf.urls.defaults import handler404, handler500
from django.contrib import admin
from django.conf import settings
from pages import settings as pages_settings
from pages.views import details

admin.autodiscover()

urlpatterns = patterns('',
    (r'^i18n/', include('django.conf.urls.i18n')),
    # We redefine urls down there to be able to use the document application
    #(r'^pages/', include('pages.urls')),
    (r'^admin/', include(admin.site.urls)),
)

if pages_settings.PAGE_USE_LANGUAGE_PREFIX:
    urlpatterns += patterns('',
        url(r'^pages/(?P<lang>[-\w]+)/(?P<path>.*)/documents/',
            include("example.documents.urls")),
        url(r'^pages/(?P<lang>[-\w]+)/(?P<path>.*)$', details,
            name='pages-details-by-path')
    )
else:
    urlpatterns += patterns('',
        url(r'^pages/$', details, name='pages-root'),
        url(r'^pages/(?P<path>.*)/documents/', include("example.documents.urls")),
        url(r'^pages/(?P<path>.*)$', details, name='pages-details-by-path')
    )

if settings.DEBUG:
    urlpatterns += patterns('',
        # Trick for Django to support static files
        # (security hole: only for Dev environement! remove this on Prod!!!)
        (r'', include('staticfiles.urls')),
    )
