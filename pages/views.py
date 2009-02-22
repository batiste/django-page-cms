# -*- coding: utf-8 -*-
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.contrib.sites.models import SITE_CACHE

from pages import settings
from pages.models import Page, Content
from pages.utils import auto_render, get_language_from_request

def details(request, page_id=None, slug=None, raise404=True,
        template_name=settings.DEFAULT_PAGE_TEMPLATE):
    """
    Example view that get the root pages for navigation, 
    and the current page if there is any root page. 
    All is rendered with the current page's template.
    """
    lang = get_language_from_request(request)
    site_id = None
    """if request.site:
        print request.site.name
        print request.site.id"""
        
    pages = Page.objects.navigation().order_by("tree_id")
    
    if pages:
        if page_id:
            current_page = get_object_or_404(
                Page.objects.published(), pk=page_id)
        elif slug:
            slug_content = Content.objects.get_content_slug_by_slug(slug)
            if slug_content and \
                slug_content.page.calculated_status in (
                    Page.PUBLISHED, Page.HIDDEN):
                current_page = slug_content.page
            else:
                raise Http404
        else:
            current_page = pages[0]
        template_name = current_page.get_template()
    else:
        raise Http404

    return template_name, locals()
details = auto_render(details)
