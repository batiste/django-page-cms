from django.conf.urls.defaults import *
from django.conf import settings
from example.documents.views import document_view
from pages.http import pages_view

urlpatterns = patterns('',
    url(r'$', pages_view(document_view), name='document_root'),
    url(r'(?P<document_id>.*)$', pages_view(document_view), name='document_details')
)