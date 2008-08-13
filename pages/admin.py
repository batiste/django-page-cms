from django.contrib import admin
from .models import Page

class PageAdmin(admin.ModelAdmin):
    list_display = ('slug', 'traductions', 'nodes')

admin.site.register(Page, PageAdmin)
