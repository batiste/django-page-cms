from django.conf.urls.defaults import *
from django_gerbi.testproj.documents.views import document_view
from django_gerbi.http import pages_view

urlpatterns = patterns('',
    url(r'^doc-(?P<document_id>[0-9]+)$', pages_view(document_view), name='document_details'),
    url(r'^$', pages_view(document_view), name='document_root'),
)