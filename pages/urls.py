from django.conf.urls.defaults import *
from django.contrib import admin
import settings
admin.autodiscover()

urlpatterns = patterns('',
    # Public pages
    (r'^$', 'pages.views.details'),
    (r'^.*?(?P<page_id>[0-9]+)/$', 'pages.views.details'),
)