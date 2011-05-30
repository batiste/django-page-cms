import authority

from django.conf.urls.defaults import url, include, patterns
from django.conf.urls.defaults import handler404, handler500
from django.contrib import admin
from django.conf import settings
from django_gerbi.views import PageSitemap, MultiLanguagePageSitemap


admin.autodiscover()
authority.autodiscover()

urlpatterns = patterns('',
    (r'^authority/', include('authority.urls')),
    (r'^i18n/', include('django.conf.urls.i18n')),

    (r'^django_gerbi/', include('django_gerbi.urls')),

    # this is only used to enable the reverse url to work with documents
    (r'^django_gerbi/(?P<path>.*)', include('django_gerbi.testproj.documents.urls')),

    (r'^admin/', include(admin.site.urls)),
    # make tests fail if a backend is not present on the system
    #(r'^search/', include('haystack.urls')),

    (r'^sitemap\.xml$', 'django.contrib.sitemaps.views.sitemap',
        {'sitemaps': {'django_gerbi':PageSitemap}}),

    (r'^sitemap2\.xml$', 'django.contrib.sitemaps.views.sitemap',
        {'sitemaps': {'django_gerbi':MultiLanguagePageSitemap}})

)

if settings.DEBUG:
    urlpatterns += patterns('',
        # Trick for Django to support static files
        # (security hole: only for Dev environement! remove this on Prod!!!)
        (r'', include('staticfiles.urls')),
    )
