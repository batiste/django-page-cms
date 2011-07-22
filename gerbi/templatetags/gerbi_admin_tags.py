"""Gerbi CMS admin template tags"""
from gerbi import settings as gerbi_settings
from gerbi.models import Content
from gerbi.templatetags.gerbi_tags import get_page_from_string_or_id

from django import template
import urllib
from django.conf import settings

register = template.Library()


def gerbi_admin_menu(context, page):
    """Return the necessary context to render the admin table of pages."""
    request = context.get('request', None)

    expanded = False
    if request and "tree_expanded" in request.COOKIES:
        cookie_string = urllib.unquote(request.COOKIES['tree_expanded'])
        if cookie_string:
            ids = [int(id) for id in
                urllib.unquote(request.COOKIES['tree_expanded']).split(',')]
            if page.id in ids:
                expanded = True
    context.update({'expanded': expanded, 'page': page})
    return context
register.inclusion_tag('admin/gerbi/page/menu.html',
    takes_context=True)(gerbi_admin_menu)


def gerbi_show_slug_with_level(context, page, lang=None, fallback=True):
    """Display slug with level by language."""
    if not lang:
        lang = context.get('lang', gerbi_settings.GERBI_DEFAULT_LANGUAGE)

    page = get_page_from_string_or_id(page, lang)
    if not page:
        return ''

    return {'content': page.slug_with_level(lang)}
register.inclusion_tag('gerbi/content.html', takes_context=True
    )(gerbi_show_slug_with_level)



def gerbi_show_revisions(context, page, content_type, lang=None):
    """Render the last 10 revisions of a page content with a list using
        the ``gerbi/revisions.html`` template"""
    if not gerbi_settings.GERBI_CONTENT_REVISION:
        return {'revisions': None}
    revisions = Content.objects.filter(page=page, language=lang,
                                type=content_type).order_by('-creation_date')
    if len(revisions) < 2:
        return {'revisions': None}
    return {'revisions': revisions[0:10]}
register.inclusion_tag('gerbi/revisions.html', takes_context=True
    )(gerbi_show_revisions)


def gerbi_language_content_up_to_date(page, language):
    """Tell if all the page content has been updated since the last
    change of the official version (settings.LANGUAGE_CODE)

    This is approximated by comparing the last modified date of any
    content in the page, not comparing each content block to its
    corresponding official language version.  That allows users to
    easily make "do nothing" changes to any content block when no
    change is required for a language.
    """
    return True
    lang_code = getattr(settings, 'LANGUAGE_CODE', None)
    if lang_code == language:
        # official version is always "up to date"
        return True
    # get the last modified date for the official version
    last_modified = page.get_content(language=lang_code, fallback=False)
    print last_modified
    if not last_modified:
        # no official version
        return True
    lang_modified = page.get_content(language=language, fallback=False)
    if not lang_modified:
        return True

    return last_modified['creation_date'] > lang_modified['creation_date']
register.filter(gerbi_language_content_up_to_date)
