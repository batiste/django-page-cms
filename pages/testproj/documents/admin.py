# Admin bindings
from django.contrib import admin
from pages.testproj.documents.models import Document


class DocumentAdmin(admin.ModelAdmin):

    list_display = ('title', 'page',)

admin.site.register(Document, DocumentAdmin)
