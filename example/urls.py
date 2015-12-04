
from django.conf import settings
from django.conf.urls import url, include, patterns
from django.conf.urls import handler404, handler500
from django.contrib import admin
from pages.views import details

admin.autodiscover()

from django.conf.urls.static import static


urlpatterns = patterns('',
    (r'^i18n/', include('django.conf.urls.i18n')),
    (r'^admin/', include(admin.site.urls)),
    #url(r'^search/', include('haystack.urls'), name='haystack_search'),
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT, show_indexes=True)
#urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT, show_indexes=True)


if 'ckeditor' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
        (r'^ckeditor/', include('ckeditor.urls')),
    )

urlpatterns += patterns('',
    # this gonna match /admin if someone forget the traling slash
    (r'^', include('pages.urls')),
)