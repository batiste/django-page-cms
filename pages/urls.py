from django.conf.urls.defaults import *
from pages.views import details

urlpatterns = patterns('',
    # Public pages
    url(r'^$', details, name='pages-root'),
    url(r'^.*?(?P<page_id>[0-9]+)/$', details, name='pages-details'),
)