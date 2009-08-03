from django.conf.urls.defaults import *
from django.contrib import admin
from django.conf import settings

admin.autodiscover()

urlpatterns = patterns('',
    (r'^i18n/', include('django.conf.urls.i18n')),
    (r'^pages/', include('pages.urls')),
    (r'^admin/', include(admin.site.urls)),
    # DEPRECATED. This function is the old way of handling URL
    #(r'^admin/(.*)', admin.site.root),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        # Trick for Django to support static files (security hole: only for Dev environement! remove this on Prod!!!)
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
        url(r'^admin_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.ADMIN_MEDIA_ROOT}),
    )
