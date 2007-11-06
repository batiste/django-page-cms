# Create your views here.

from pages.models import Page, Language, Content
from pages.utils import auto_render
from django.contrib.admin.views.decorators import staff_member_required
from django import newforms as forms
    
@auto_render
def slug(request, slug=None):
    template = None
    if slug:
        current_page = Page.published.get(slug=slug)
        template = current_page.get_template()
    pages = Page.published.filter(parent__isnull=True)
    if not template:
        template = 'index.html'
    return template, locals()
    
