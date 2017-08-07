
from django.conf.urls import url, include
from django.conf.urls import handler404, handler500
from django.contrib import admin
from django.conf import settings
from django.contrib.sitemaps.views import sitemap
from pages.views import PageSitemap, MultiLanguagePageSitemap


admin.autodiscover()

urlpatterns = [
    url(r'^i18n/', include('django.conf.urls.i18n')),

    url(r'^pages/', include('pages.urls')),

    # this is only used to enable the reverse url to work with documents
    url(r'^pages/(?P<path>.*)', include('pages.testproj.documents.urls')),

    url(r'^admin/', include(admin.site.urls)),
    # make tests fail if a backend is not present on the system
    #(r'^search/', include('haystack.urls')),

    url(r'^sitemap\.xml$', sitemap,
        {'sitemaps': {'pages':PageSitemap}}),

    url(r'^sitemap2\.xml$', sitemap,
        {'sitemaps': {'pages':MultiLanguagePageSitemap}})
]
