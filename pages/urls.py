# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
from pages.views import details, alias_wrapper
from pages import settings

urlpatterns = patterns('',
    # Public pages
    url(r'^$', details, name='pages-root'),
)

if settings.PAGE_USE_LANGUAGE_PREFIX:
    urlpatterns += patterns('',
        url(r'^(?P<lang>[-\w]+)/(?P<path>.*)$', alias_wrapper,
            name='pages-details-by-path'),
    )
else:
    urlpatterns += patterns('',
        url(r'^(?P<path>.*)$', alias_wrapper,
            name='pages-details-by-path'),
    )