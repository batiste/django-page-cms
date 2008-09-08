from pages.models import Page, Language, Content
from pages.utils import auto_render
from django.contrib.admin.views.decorators import staff_member_required
from django import forms
    
@auto_render
def details(request, page_id=None):
    template = None
    pages = Page.objects.filter(parent__isnull=True).order_by("tree_id")
    if page_id:
        current_page = Page.objects.get(id=int(page_id))
        template = current_page.get_template()
    else:
        current_page = Page.objects.get(id=int(2))
    
    if not template:
        import settings
        template = settings.DEFAULT_PAGE_TEMPLATE
    
    return template, locals()
    
