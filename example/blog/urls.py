from django.conf.urls import url
from blog import views
from django.urls import include, path, re_path

urlpatterns = [
  url(r'^category/(?P<tag_id>[0-9]+)$', views.category_view, name='blog_category_view'),
  url(r'^$', views.blog_index, name='blog_index')
]