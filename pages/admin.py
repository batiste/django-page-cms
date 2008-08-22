from django.contrib import admin
from .models import Page, Language
import settings

class PageAdmin(admin.ModelAdmin):
    pass

class LanguageAdmin(admin.ModelAdmin):
    pass

class PermissionAdmin(admin.ModelAdmin):
    pass

admin.site.register(Page, PageAdmin)
admin.site.register(Language, LanguageAdmin)
if settings.PAGE_PERMISSION:
    from .models import PagePermission
    admin.site.register(PagePermission, PermissionAdmin)