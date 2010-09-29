"""Default example views"""
from django.http import Http404, HttpResponsePermanentRedirect
from pages import settings
from pages.models import Page, PageAlias
from pages.http import auto_render, get_language_from_request
from pages.http import get_slug_and_relative_path
from pages.urlconf_registry import get_urlconf
from django.core.urlresolvers import resolve
from django.utils import translation


class Details(object):
    """
    This view get the root pages for navigation
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

    def __call__(self, request, path=None, lang=None, delegation=True,
            **kwargs):

        pages_navigation = self.get_navigation(request)
        current_page = False
        lang = self.get_language(lang, request)

        # if the path is not defined, we assume that the user
        # is using the view in a non usual way and fallback onto the
        # the full request path.
        if path is None:
            path = request.path

        context = {
            'path': path,
            'pages_navigation': pages_navigation,
            'lang': lang,
        }

        is_staff = self.is_user_staff(request)
        if path:
            current_page = Page.objects.from_path(path, lang,
                exclude_drafts=(not is_staff))
        elif pages_navigation:
            current_page = Page.objects.root()[0]

        # if no pages has been found, we will try to find it via an Alias
        if not current_page:
            alias = PageAlias.objects.from_path(request, path, lang)
            if alias:
                url = alias.page.get_url_path(lang)
                return HttpResponsePermanentRedirect(url)
            raise Http404

        # If unauthorized to see the pages, raise a 404
        if not is_staff and not current_page.visible:
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

        self.extra_context(request, context)

        # if there is a delegation to another view,
        # call this view instead.
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

    def get_navigation(self, request):
        """Get the pages that are at the root level."""
        return Page.objects.navigation().order_by("tree_id")

    def get_language(self, lang, request):
        """Deal with the multiple corner case of choosing the language."""

        # Can be an empty string or None
        if not lang:
            lang = get_language_from_request(request)

        # Raise a 404 if the language is not in not in the list
        if lang not in [key for (key, value) in settings.PAGE_LANGUAGES]:
            raise Http404

        # We're going to serve CMS pages in language lang;
        # make django gettext use that language too
        if lang and translation.check_for_language(lang):
            translation.activate(lang)

        return lang

    def is_user_staff(self, request):
        """Return True if the user is staff."""
        return request.user.is_authenticated() and request.user.is_staff

    def extra_context(self, request, context):
        """Call the PAGE_EXTRA_CONTEXT function if there is one."""
        if settings.PAGE_EXTRA_CONTEXT:
            context.update(settings.PAGE_EXTRA_CONTEXT())

details = auto_render(Details())
