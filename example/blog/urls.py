from django.conf.urls import re_path
from blog import views
from django.urls import include, path

urlpatterns = [
  re_path(r'^category/(?P<tag_id>[0-9]+)$', views.category_view, name='blog_category_view'),
  re_path(r'^$', views.blog_index, name='blog_index')
]