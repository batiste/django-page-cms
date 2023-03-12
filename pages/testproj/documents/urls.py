from django.urls import re_path
from pages.testproj.documents.views import document_view

urlpatterns = [
    re_path(r'^doc-(?P<document_id>[0-9]+)$', document_view, name='document_details'),
    re_path(r'^$', document_view, name='document_root'),
]
