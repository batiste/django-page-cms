"""Default example views"""
from django.http import Http404, HttpResponsePermanentRedirect
from pages import settings
from pages.models import Page, PageAlias
from pages.http import auto_render, get_language_from_request
from pages.http import get_slug_and_relative_path
from pages.urlconf_registry import get_urlconf
from django.core.urlresolvers import resolve

def details(request, path=None, lang=None, delegation=True, **kwargs):
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
    
    pages_navigation = Page.objects.navigation().order_by("tree_id")
    current_page = False
    template_name = settings.PAGE_DEFAULT_TEMPLATE

    if path is None:
        slug, path, lang = get_slug_and_relative_path(request.path, lang)

    # Can be an empty string or None
    if not lang:
        lang = get_language_from_request(request)

    context = {
        'path': path,
        'pages_navigation': pages_navigation,
        'lang': lang,
    }

    if lang not in [key for (key, value) in settings.PAGE_LANGUAGES]:
        raise Http404

    is_user_staff = request.user.is_authenticated() and request.user.is_staff
    if path:
        current_page = Page.objects.from_path(path, lang,
            exclude_drafts=(not is_user_staff))
    elif pages_navigation:
        current_page = Page.objects.root()[0]

    # if no pages has been found, we will try to find it via an Alias
    if not current_page:
        alias = PageAlias.objects.from_path(request, path, lang)
        if alias:
            url = alias.page.get_url_path(lang)
            return HttpResponsePermanentRedirect(url)
        raise Http404

    if ((not is_user_staff) and
            current_page.calculated_status in (Page.DRAFT, Page.EXPIRED)):
        raise Http404

    if current_page.redirect_to_url:
        return HttpResponsePermanentRedirect(current_page.redirect_to_url)
    
    if current_page.redirect_to:
        return HttpResponsePermanentRedirect(
            current_page.redirect_to.get_url_path(lang))
    
    template_name = current_page.get_template()
    
    if request.is_ajax():
        template_name = "body_%s" % template_name

    if current_page:
        context['current_page'] = current_page

    if settings.PAGE_EXTRA_CONTEXT:
        context.update(settings.PAGE_EXTRA_CONTEXT())

    if delegation and current_page.delegate_to:
        urlconf = get_urlconf(current_page.delegate_to)
        result = resolve('/', urlconf)
        if len(result):
            view, args, kwargs = result
            kwargs['current_page'] = current_page
            kwargs['path'] = path
            kwargs['lang'] = lang
            kwargs['pages_navigation'] = pages_navigation
            return view(
                request,
                *args,
                **kwargs
            )

    return template_name, context

details = auto_render(details)
