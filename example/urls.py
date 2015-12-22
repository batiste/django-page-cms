
from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls import handler404, handler500
from django.contrib import admin
from pages.views import details

admin.autodiscover()

from django.conf.urls.static import static


urlpatterns = [
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^admin/', include(admin.site.urls)),
    #url(r'^search/', include('haystack.urls'), name='haystack_search'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT, show_indexes=True)
#urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT, show_indexes=True)


if 'ckeditor' in settings.INSTALLED_APPS:
    urlpatterns += [
        url(r'^ckeditor/', include('ckeditor.urls')),
    ]

urlpatterns += [
    # this gonna match /admin if someone forget the traling slash
    url(r'^', include('pages.urls')),
]