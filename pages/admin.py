from django.contrib import admin
from .models import Page, Language

class PageAdmin(admin.ModelAdmin):
    pass

class LanguageAdmin(admin.ModelAdmin):
    pass

admin.site.register(Page, PageAdmin)
admin.site.register(Language, LanguageAdmin)
