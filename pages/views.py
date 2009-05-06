# -*- coding: utf-8 -*-
from django.http import Http404, HttpResponsePermanentRedirect
from django.shortcuts import get_object_or_404
from django.contrib.sites.models import SITE_CACHE
from pages import settings
from pages.models import Page, Content
from pages.utils import auto_render, get_language_from_request, get_page_from_slug


def details(request, slug=None, lang=None, ajax=False):
    """
    This example view get the root pages for navigation
    and the current page to display if there is any.

    All is rendered with the current page's template.

    This view use the auto_render decorator. It means
    that you can use the only_context extra parameter to get
    only the local variables of this view without rendering
    the template.

    >>> from pages.views import details
    >>> from pages.utils import get_request_mock
    >>> request = get_request_mock()
    >>> context = details(request, only_context=True)

    This can be usefull if you want to write your own
    view and reuse the following code without having to
    copy and paste it.
    """
    pages = Page.objects.navigation().order_by("tree_id")
    current_page = False

    if slug:
        current_page = get_page_from_slug(slug, request, lang)
    elif pages:
        current_page = pages[0]

    if not current_page:
        raise Http404

    if not (request.user.is_authenticated() and request.user.is_staff) and \
        current_page.calculated_status in (Page.DRAFT, Page.EXPIRED):
        raise Http404
    
    if not lang:
        lang = get_language_from_request(request, current_page)
    
    if current_page.redirect_to:
        # return this object if you want to activate redirections
        http_redirect = HttpResponsePermanentRedirect(
            current_page.redirect_to.get_absolute_url(lang))
    
    template_name = current_page.get_template()
    
    if ajax:
        new_template_name = "body_%s" % template_name
        return new_template_name, locals()
    
    return template_name, locals()
    
details = auto_render(details)