import authority

from django.conf.urls.defaults import url, include, patterns
from django.conf.urls.defaults import handler404, handler500
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from pages.views import details

from pages.urlconf_registry import register_urlconf
register_urlconf('test', 'pages.testsproject.documents.urls')

admin.autodiscover()
authority.autodiscover()

urlpatterns = patterns('',
    (r'^authority/', include('authority.urls')),
    (r'^i18n/', include('django.conf.urls.i18n')),
    (r'^admin/', include(admin.site.urls)),

    # make tests fail if a backend is not present on the system
    (r'^search/', include('haystack.urls')),

)

urlpatterns += staticfiles_urlpatterns()

urlpatterns += patterns('',
    # this gonna match /admin if someone forget the traling slash
    (r'^', include('pages.urls')),
)
