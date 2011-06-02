# Admin bindings
from django.contrib import admin
from django_gerbi.testproj.documents.models import Document

class DocumentAdmin(admin.ModelAdmin):

    list_display   = ('title', 'page',)

admin.site.register(Document, DocumentAdmin)
