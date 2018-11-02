
from django.conf import settings
from django.conf.urls import url
from django.urls import include, path, re_path
from django.conf.urls.static import static
from django.contrib import admin

admin.autodiscover()


urlpatterns = [
    url(r'^i18n/', include('django.conf.urls.i18n')),
    # url(r'^grappelli/', include('grappelli.urls')),  # grappelli URLS
    url(r'^admin/', admin.site.urls),
]

try:
	import haystack
	urlpatterns += [url(r'^search/', include('haystack.urls'), name='haystack_search')]
except ImportError:
	pass

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT, show_indexes=True)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT, show_indexes=True)


if 'ckeditor' in settings.INSTALLED_APPS:
    urlpatterns += [
        url(r'^ckeditor/', include('ckeditor.urls')),
    ]

urlpatterns += [
    # this will match /admin if someone forget the traling slash
    url(r'^', include('pages.urls')),
]
