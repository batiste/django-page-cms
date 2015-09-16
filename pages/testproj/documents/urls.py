from django.conf.urls import *
from pages.testproj.documents.views import document_view

urlpatterns = patterns('',
    url(r'^doc-(?P<document_id>[0-9]+)$', document_view, name='document_details'),
    url(r'^$', document_view, name='document_root'),
)