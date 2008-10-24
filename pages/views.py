from pages.models import Page, Language, Content
from pages.utils import auto_render
from django.contrib.admin.views.decorators import staff_member_required
from django import forms
from django.http import Http404
import settings

@auto_render
def details(request, page_id=None):
    template = None
    lang = Language.get_from_request(request)
    pages = Page.objects.filter(parent__isnull=True).order_by("tree_id")
    if len(pages) > 0:
        if page_id:
            try:
                current_page = Page.objects.get(id=int(page_id), status=1)
            except Page.DoesNotExist:
                raise Http404
        else:
            # get the first root page
            current_page = pages[0]
        template = current_page.get_template()
    else:
        template = settings.DEFAULT_PAGE_TEMPLATE
    
    return template, locals()
