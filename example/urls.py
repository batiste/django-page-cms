
from django.conf import settings
from django.conf.urls import url
from django.urls import include, path, re_path
from django.conf.urls.static import static
from django.contrib import admin
from pages import views

from pages.urlconf_registry import register_urlconf
register_urlconf('blog', 'blog.urls', label='Blog index')

urlpatterns = [
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^admin/', admin.site.urls),
]

try:
	import haystack
	urlpatterns += [url(r'^search/', include('haystack.urls'), name='haystack_search')]
except ImportError:
	pass

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += [
    url(r'^$', views.details, {'path': '', 'name': 'pages-root'}),
    url(r'^', include('pages.urls')),
]

admin.site.site_header = 'Gerbi Admin'
