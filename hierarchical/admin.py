from django.contrib import admin
from .models import HierarchicalNode

class HierarchicalNodeAdmin(admin.ModelAdmin):
    pass

admin.site.register(HierarchicalNode, HierarchicalNodeAdmin)
