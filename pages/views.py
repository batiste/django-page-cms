# Create your views here.

from pages.models import Page, Language, Content
from pages.utils import auto_render
from django.contrib.admin.views.decorators import staff_member_required
from django import newforms as forms
    
@auto_render
def details(request, page_id=None):
    template = None
    if page_id:
        current_page = Page.published.get(id=page_id)
        template = current_page.get_template()
    pages = Page.published.filter(parent__isnull=True)
    if not template:
        import settings
        template = settings.DEFAULT_PAGE_TEMPLATE
    return template, locals()
    
