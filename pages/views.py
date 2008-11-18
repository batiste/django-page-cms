from django.http import Http404
from django.shortcuts import get_object_or_404, render_to_response

from pages import settings
from pages.models import Page, Content
from pages.utils import auto_render, get_template_from_request, get_language_from_request

def details(request, page_id=None, slug=None, 
        template_name=settings.DEFAULT_PAGE_TEMPLATE):
    lang = get_language_from_request(request)
    pages = Page.on_site.root().order_by("tree_id")
    if pages.count():
        if page_id:
            current_page = get_object_or_404(Page.on_site.published(), pk=page_id)
        elif slug:
            content = Content.objects.get_page_slug(slug)
            if content and content.page.calculated_status == Page.PUBLISHED:
                current_page = content.page
            else:
                raise Http404
        else:
            current_page = pages[0]
        template_name = get_template_from_request(request, current_page)
    else:
        current_page = None
    return template_name, locals()
details = auto_render(details)
