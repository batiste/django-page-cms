"""Default example views"""
from django.http import Http404, HttpResponsePermanentRedirect
from django.shortcuts import get_object_or_404
from django.contrib.sites.models import SITE_CACHE
from pages import settings
from pages.models import Page, Content, PageAlias
from pages.http import auto_render, get_language_from_request
from pages.http import get_slug_and_relative_path

def details(request, path=None, lang=None):
    """This view get the root pages for navigation
    and the current page to display if there is any.

    All is rendered with the current page's template.

    This view use the auto_render decorator. It means
    that you can use the only_context extra parameter to get
    only the local variables of this view without rendering
    the template.

    >>> from pages.views import details
    >>> context = details(request, only_context=True)

    This can be usefull if you want to write your own
    view. You can reuse the following code without having to
    copy and paste it."""
    
    pages = Page.objects.navigation().order_by("tree_id")
    current_page = False
    template_name = settings.DEFAULT_PAGE_TEMPLATE

    if path is None:
        slug, path, lang = get_slug_and_relative_path(request.path, lang)

    if lang is None:
        lang = get_language_from_request(request)

    context = {
        'path': path,
        'pages': pages,
        'lang': lang,
    }

    if lang not in [key for (key, value) in settings.PAGE_LANGUAGES]:
        raise Http404

    exclude_drafts = not(request.user.is_authenticated() and request.user.is_staff)
    if path:
        current_page = Page.objects.from_path(path, lang, exclude_drafts=exclude_drafts)
    elif pages:
        current_page = Page.objects.published().order_by("tree_id")[0]

    # if no pages has been found, we will try to find it via an Alias
    if not current_page:
        alias = PageAlias.objects.from_path(request, path, lang)
        if alias:
            url = alias.page.get_absolute_url(lang)
            return HttpResponsePermanentRedirect(url)
        raise Http404

    if not (request.user.is_authenticated() and request.user.is_staff) and \
            current_page.calculated_status in (Page.DRAFT, Page.EXPIRED):
        raise Http404

    if current_page.redirect_to_url:
        return HttpResponsePermanentRedirect(current_page.redirect_to_url)
    
    if current_page.redirect_to:
        return HttpResponsePermanentRedirect(
            current_page.redirect_to.get_absolute_url(lang))
    
    template_name = current_page.get_template()
    
    if request.is_ajax():
        template_name = "body_%s" % template_name

    if current_page:
        context['current_page'] = current_page

    if settings.PAGE_EXTRA_CONTEXT:
        context.update(settings.PAGE_EXTRA_CONTEXT())
        
    return template_name, context

details = auto_render(details)
