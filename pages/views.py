from pages.models import Page, Language, Content
from hierarchical.utils import auto_render
from django.contrib.admin.views.decorators import staff_member_required
from django import forms
from hierarchical.models import HierarchicalNode, HierarchicalObject
    
@auto_render
def details(request, page_id=None):
    template = None
    pages = HierarchicalNode.get_first_level_objects(Page)
    if page_id:
        current_page = Page.objects.get(id=int(page_id))
        template = current_page.get_template()
        nodes = HierarchicalNode.get_nodes_by_object(current_page)
        # it's possible that a page has no node
        if len(nodes):
            node = nodes[0]
            all_objects = node.get_objects()
    
    if not template:
        import settings
        template = settings.DEFAULT_PAGE_TEMPLATE
    
    return template, locals()
    
