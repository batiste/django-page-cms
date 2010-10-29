import authority

from django.conf.urls.defaults import url, include, patterns
from django.conf.urls.defaults import handler404, handler500
from django.contrib import admin
from django.conf import settings
from pages.views import PageSitemap, MultiLanguagePageSitemap


admin.autodiscover()
authority.autodiscover()

urlpatterns = patterns('',
    (r'^authority/', include('authority.urls')),
    (r'^i18n/', include('django.conf.urls.i18n')),

    (r'^pages/', include('pages.urls')),

    # this is only used to enable the reverse url to work with documents
    (r'^pages/(?P<path>.*)', include('pages.testproj.documents.urls')),

    (r'^admin/', include(admin.site.urls)),
    # make tests fail if a backend is not present on the system
    #(r'^search/', include('haystack.urls')),

    (r'^sitemap\.xml$', 'django.contrib.sitemaps.views.sitemap',
        {'sitemaps': {'pages':PageSitemap}}),

    (r'^sitemap2\.xml$', 'django.contrib.sitemaps.views.sitemap',
        {'sitemaps': {'pages':MultiLanguagePageSitemap}})

)

if settings.DEBUG:
    urlpatterns += patterns('',
        # Trick for Django to support static files
        # (security hole: only for Dev environement! remove this on Prod!!!)
        (r'', include('staticfiles.urls')),
    )
