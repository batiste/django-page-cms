import authority

from django.conf import settings
from django.conf.urls import url, include, patterns
from django.conf.urls import handler404, handler500
from django.conf.urls.static import static
from django.contrib import admin
from pages.views import details

admin.autodiscover()
authority.autodiscover()

urlpatterns = patterns('',
    #(r'^authority/', include('authority.urls')),
    (r'^i18n/', include('django.conf.urls.i18n')),
    (r'^admin/', include(admin.site.urls)),
    #(r'^grappelli/', include('grappelli.urls')),
    # make tests fail if a backend is not present on the system
    #url(r'^search/', include('haystack.urls'), name='haystack_search'),

)

if 'ckeditor' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
        (r'^ckeditor/', include('ckeditor.urls')),
    )

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += patterns('',
    # this gonna match /admin if someone forget the traling slash
    (r'^', include('pages.urls')),
)
