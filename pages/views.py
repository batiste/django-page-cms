# -*- coding: utf-8 -*-
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.contrib.sites.models import SITE_CACHE
from pages import settings
from pages.models import Page, Content
from pages.utils import auto_render, get_language_from_request, get_page_from_slug

def details(request, slug=None, lang=None):
    """
    Example view that get the root pages for navigation,
    and the current page if there is any root page.
    All is rendered with the current page's template.
    """
    pages = Page.objects.navigation().order_by("tree_id")
    current_page = False

    if pages:
        if slug:
            current_page = get_page_from_slug(slug, request, lang)
        else:
            current_page = pages[0]

    if not current_page:
        raise Http404

    if not current_page.calculated_status in (Page.PUBLISHED, Page.HIDDEN):
        raise Http404

    if not lang:
        lang = get_language_from_request(request, current_page)

    template_name = current_page.get_template()
    return template_name, locals()
details = auto_render(details)