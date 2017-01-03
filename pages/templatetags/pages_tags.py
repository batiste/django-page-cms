"""Page CMS page_tags template tags"""
from django import template
from django.utils.safestring import SafeText
from django.template import TemplateSyntaxError
from django.conf import settings
from django.utils.text import unescape_string_literal
from django import forms
from django.template.loader import get_template
from django.contrib.staticfiles.templatetags.staticfiles import static

from pages import settings as pages_settings
from pages.models import Content, Page
from pages.placeholders import (
    PlaceholderNode, ImagePlaceholderNode, FilePlaceholderNode
)
from pages.placeholders import ContactPlaceholderNode, MarkdownPlaceholderNode
from pages.placeholders import JsonPlaceholderNode, parse_placeholder
from six.moves import urllib
import six
from pages.utils import get_placeholders


register = template.Library()


def get_page_from_string_or_id(page_string, lang=None):
    """Return a Page object from a slug or an id."""
    if type(page_string) == int:
        return Page.objects.get(pk=int(page_string))
    # if we have a string coming from some templates templates
    if (isinstance(page_string, SafeText) or
            isinstance(page_string, six.string_types)):
        if page_string.isdigit():
            return Page.objects.get(pk=int(page_string))
        return Page.objects.from_path(page_string, lang)
    # in any other case we return the input becasue it's probably
    # a Page object.
    return page_string


def _get_content(context, page, content_type, lang, fallback=True):
    """Helper function used by ``PlaceholderNode``."""
    if not page:
        return ''

    if not lang and 'lang' in context:
        lang = context.get('lang', pages_settings.PAGE_DEFAULT_LANGUAGE)

    page = get_page_from_string_or_id(page, lang)

    if not page:
        return ''

    content = Content.objects.get_content(page, lang, content_type, fallback)
    return content


"""Filters"""


def has_content_in(page, language):
    """Fitler that return ``True`` if the page has any content in a
    particular language.

    :param page: the current page
    :param language: the language you want to look at
    """
    if page is None:
        return False
    return Content.objects.filter(page=page, language=language).count() > 0


register.filter(has_content_in)


"""Inclusion tags"""


def pages_menu(context, page, url='/'):
    """Render a nested list of all the descendents of the given page,
    including this page.

    :param page: the page where to start the menu from.
    :param url: not used anymore.
    """
    lang = context.get('lang', pages_settings.PAGE_DEFAULT_LANGUAGE)
    page = get_page_from_string_or_id(page, lang)
    if page:
        children = page.get_children_for_frontend()
        context.update({'children': children, 'page': page})
    return context


pages_menu = register.inclusion_tag('pages/menu.html',
                                    takes_context=True)(pages_menu)


def pages_sub_menu(context, page, url='/'):
    """Get the root page of the given page and
    render a nested list of all root's children pages.
    Good for rendering a secondary menu.

    :param page: the page where to start the menu from.
    :param url: not used anymore.
    """
    lang = context.get('lang', pages_settings.PAGE_DEFAULT_LANGUAGE)
    page = get_page_from_string_or_id(page, lang)
    if page:
        root = page.get_root()
        children = root.get_children_for_frontend()
        context.update({'children': children, 'page': page})
    return context


pages_sub_menu = register.inclusion_tag('pages/sub_menu.html',
                                        takes_context=True)(pages_sub_menu)


def pages_siblings_menu(context, page, url='/'):
    """Get the parent page of the given page and render a nested list of its
    child pages. Good for rendering a secondary menu.

    :param page: the page where to start the menu from.
    :param url: not used anymore.
    """
    lang = context.get('lang', pages_settings.PAGE_DEFAULT_LANGUAGE)
    page = get_page_from_string_or_id(page, lang)
    if page:
        siblings = page.get_siblings()
        context.update({'children': siblings, 'page': page})
    return context


pages_siblings_menu = register.inclusion_tag(
    'pages/sub_menu.html',
    takes_context=True)(pages_siblings_menu)


def pages_admin_menu(context, page):
    """Render the admin table of pages."""
    request = context.get('request', None)

    expanded = False
    if request and "tree_expanded" in request.COOKIES:
        cookie_string = urllib.parse.unquote(request.COOKIES['tree_expanded'])
        if cookie_string:
            ids = [
                int(id) for id in
                urllib.parse.unquote(
                    request.COOKIES['tree_expanded']).split(',')
            ]
            if page.id in ids:
                expanded = True
    context.update({'expanded': expanded, 'page': page})
    return context


pages_admin_menu = register.inclusion_tag(
    'admin/pages/page/menu.html', takes_context=True
)(pages_admin_menu)


def show_content(context, page, content_type, lang=None, fallback=True):
    """Display a content type from a page.

    Example::

        {% show_content page_object "title" %}

    You can also use the slug of a page::

        {% show_content "my-page-slug" "title" %}

    Or even the id of a page::

        {% show_content 10 "title" %}

    :param page: the page object, slug or id
    :param content_type: content_type used by a placeholder
    :param lang: the wanted language
        (default None, use the request object to know)
    :param fallback: use fallback content from other language
    """
    return {'content': _get_content(
        context, page, content_type, lang, fallback)
    }


show_content = register.inclusion_tag('pages/content.html',
                                      takes_context=True)(show_content)


def show_absolute_url(context, page, lang=None):
    """
    Show the url of a page in the right language

    Example ::

        {% show_absolute_url page_object %}

    You can also use the slug of a page::

        {% show_absolute_url "my-page-slug" %}

    Keyword arguments:
    :param page: the page object, slug or id
    :param lang: the wanted language \
        (defaults to `settings.PAGE_DEFAULT_LANGUAGE`)
    """
    if not lang:
        lang = context.get('lang', pages_settings.PAGE_DEFAULT_LANGUAGE)
    page = get_page_from_string_or_id(page, lang)
    if not page:
        return {'content': ''}
    url = page.get_url_path(language=lang)
    if url:
        return {'content': url}
    return {'content': ''}


show_absolute_url = register.inclusion_tag(
    'pages/content.html',
    takes_context=True)(show_absolute_url)


def show_revisions(context, page, content_type, lang=None):
    """Render the last 10 revisions of a page content with a list using
        the ``pages/revisions.html`` template"""
    if (not pages_settings.PAGE_CONTENT_REVISION or
            content_type in pages_settings.PAGE_CONTENT_REVISION_EXCLUDE_LIST):
        return {'revisions': None}
    revisions = Content.objects.filter(
        page=page, language=lang,
        type=content_type).order_by('-creation_date')
    if len(revisions) < 2:
        return {'revisions': None}
    return {'revisions': revisions[0:10]}


show_revisions = register.inclusion_tag(
    'pages/revisions.html',
    takes_context=True)(show_revisions)


def pages_dynamic_tree_menu(context, page, url='/'):
    """
    Render a "dynamic" tree menu, with all nodes expanded which are either
    ancestors or the current page itself.

    Override ``pages/dynamic_tree_menu.html`` if you want to change the
    design.

    :param page: the current page
    :param url: not used anymore
    """
    lang = context.get('lang', pages_settings.PAGE_DEFAULT_LANGUAGE)
    page = get_page_from_string_or_id(page, lang)
    children = None
    if page and 'current_page' in context:
        current_page = context['current_page']
        # if this node is expanded, we also have to render its children
        # a node is expanded if it is the current node or one of its ancestors
        if(
            page.tree_id == current_page.tree_id and
            page.lft <= current_page.lft and
            page.rght >= current_page.rght
        ):
            children = page.get_children_for_frontend()
    context.update({'children': children, 'page': page})
    return context


pages_dynamic_tree_menu = register.inclusion_tag(
    'pages/dynamic_tree_menu.html',
    takes_context=True
)(pages_dynamic_tree_menu)


def pages_breadcrumb(context, page, url='/'):
    """
    Render a breadcrumb like menu.

    Override ``pages/breadcrumb.html`` if you want to change the
    design.

    :param page: the current page
    :param url: not used anymore
    """
    lang = context.get('lang', pages_settings.PAGE_DEFAULT_LANGUAGE)
    page = get_page_from_string_or_id(page, lang)
    pages_navigation = None
    if page:
        pages_navigation = page.get_ancestors()
    context.update({'pages_navigation': pages_navigation, 'page': page})
    return context


pages_breadcrumb = register.inclusion_tag(
    'pages/breadcrumb.html',
    takes_context=True
)(pages_breadcrumb)


"""Tags"""


class GetPageNode(template.Node):
    """get_page Node"""
    def __init__(self, page_filter, varname):
        self.page_filter = page_filter
        self.varname = varname

    def render(self, context):
        page_or_id = self.page_filter.resolve(context)
        page = get_page_from_string_or_id(page_or_id)
        context[self.varname] = page
        return ''


def do_get_page(parser, token):
    """Retrieve a page and insert into the template's context.

    Example::

        {% get_page "news" as news_page %}

    :param page: the page object, slug or id
    :param name: name of the context variable to store the page in
    """
    bits = token.split_contents()
    if 4 != len(bits):
        raise TemplateSyntaxError('%r expects 4 arguments' % bits[0])
    if bits[-2] != 'as':
        raise TemplateSyntaxError(
            '%r expects "as" as the second argument' % bits[0])
    page_filter = parser.compile_filter(bits[1])
    varname = bits[-1]
    return GetPageNode(page_filter, varname)


do_get_page = register.tag('get_page', do_get_page)


class GetContentNode(template.Node):
    """Get content node"""
    def __init__(self, page, content_type, varname, lang, lang_filter):
        self.page = page
        self.content_type = content_type
        self.varname = varname
        self.lang = lang
        self.lang_filter = lang_filter

    def render(self, context):
        if self.lang_filter:
            self.lang = self.lang_filter.resolve(context)
        context[self.varname] = _get_content(
            context,
            self.page.resolve(context),
            self.content_type.resolve(context),
            self.lang
        )
        return ''


def do_get_content(parser, token):
    """Retrieve a Content object and insert it into the template's context.

    Example::

        {% get_content page_object "title" as content %}

    You can also use the slug of a page::

        {% get_content "my-page-slug" "title" as content %}

    Syntax::

        {% get_content page type [lang] as name %}

    :param page: the page object, slug or id
    :param type: content_type used by a placeholder
    :param name: name of the context variable to store the content in
    :param lang: the wanted language
    """
    bits = token.split_contents()
    if not 5 <= len(bits) <= 6:
        raise TemplateSyntaxError('%r expects 4 or 5 arguments' % bits[0])
    if bits[-2] != 'as':
        raise TemplateSyntaxError(
            '%r expects "as" as the second last argument' % bits[0])
    page = parser.compile_filter(bits[1])
    content_type = parser.compile_filter(bits[2])
    varname = bits[-1]
    lang = None
    lang_filter = None
    if len(bits) == 6:
        lang = bits[3]
    else:
        lang_filter = parser.compile_filter("lang")
    return GetContentNode(page, content_type, varname, lang, lang_filter)


do_get_content = register.tag('get_content', do_get_content)


class LoadPagesNode(template.Node):
    """Load page node."""
    def render(self, context):
        if 'pages_navigation' not in context:
            pages = Page.objects.navigation().order_by("tree_id")
            context.update({'pages_navigation': pages})
        if 'current_page' not in context:
            context.update({'current_page': None})
        return ''


def do_load_pages(parser, token):
    """Load the navigation pages, lang, and current_page variables into the
    current context.

    Example::

        <ul>
            {% load_pages %}
            {% for page in pages_navigation %}
                {% pages_menu page %}
            {% endfor %}
        </ul>
    """
    return LoadPagesNode()


do_load_pages = register.tag('load_pages', do_load_pages)


class LoadEditNode(template.Node):
    """Load edit node."""

    def render(self, context):
        request = context.get('request')
        if not request.user.is_staff:
            return ''
        template_name = context.get('template_name')
        placeholders = get_placeholders(template_name)
        page = context.get('current_page')
        if not page:
            return ''
        lang = context.get('lang', pages_settings.PAGE_DEFAULT_LANGUAGE)
        form = forms.Form()
        for p in placeholders:
            field = p.get_field(
                page, lang, initial=p.get_content_from_context(context))
            form.fields[p.name] = field

        template = get_template('pages/inline-edit.html')
        with context.push():
            context['form'] = form
            context['edit_enabled'] = request.COOKIES.get('enable_edit_mode')
            content = template.render(context)

        return content


def do_load_edit(parser, token):
    """
    """
    return LoadEditNode()


do_load_edit = register.tag('pages_edit_init', do_load_edit)


class LoadEditMediaNode(template.Node):
    """Load edit node."""

    def render(self, context):
        request = context.get('request')
        if not request.user.is_staff:
            return ''
        template_name = context.get('template_name')
        placeholders = get_placeholders(template_name)
        page = context.get('current_page')
        lang = context.get('lang', pages_settings.PAGE_DEFAULT_LANGUAGE)
        form = forms.Form()
        for p in placeholders:
            field = p.get_field(page, lang)
            form.fields[p.name] = field

        link = '<link href="{}" type="text/css" media="all" rel="stylesheet" />'.format(
            static('pages/css/inline-edit.css')
            )

        return "{}{}".format(form.media, link)


def do_load_edit_media(parser, token):
    """
    """
    return LoadEditMediaNode()


do_load_edit = register.tag('pages_edit_media', do_load_edit_media)


def do_placeholder(parser, token):
    """
    Method that parse the placeholder template tag.

    Syntax::

        {% placeholder <name> [on <page>] [with <widget>] \
[parsed] [as <varname>] %}

    Example usage::

        {% placeholder about %}
        {% placeholder body with TextArea as body_text %}
        {% placeholder welcome with TextArea parsed as welcome_text %}
        {% placeholder teaser on next_page with TextArea parsed %}
    """
    name, params = parse_placeholder(parser, token)

    return PlaceholderNode(name, **params)
register.tag('placeholder', do_placeholder)


def do_markdownlaceholder(parser, token):
    """
    Method that parse the markdownplaceholder template tag.
    """
    name, params = parse_placeholder(parser, token)
    return MarkdownPlaceholderNode(name, **params)
register.tag('markdownplaceholder', do_markdownlaceholder)


def do_imageplaceholder(parser, token):
    """
    Method that parse the imageplaceholder template tag.
    """
    name, params = parse_placeholder(parser, token)
    return ImagePlaceholderNode(name, **params)
register.tag('imageplaceholder', do_imageplaceholder)


def do_fileplaceholder(parser, token):
    """
    Method that parse the fileplaceholder template tag.
    """
    name, params = parse_placeholder(parser, token)
    return FilePlaceholderNode(name, **params)
register.tag('fileplaceholder', do_fileplaceholder)


def do_contactplaceholder(parser, token):
    """
    Method that parse the contactplaceholder template tag.
    """
    name, params = parse_placeholder(parser, token)
    return ContactPlaceholderNode(name, **params)
register.tag('contactplaceholder', do_contactplaceholder)


def do_jsonplaceholder(parser, token):
    """
    Method that parse the contactplaceholder template tag.
    """
    name, params = parse_placeholder(parser, token)
    return JsonPlaceholderNode(name, **params)


register.tag('jsonplaceholder', do_jsonplaceholder)


def language_content_up_to_date(page, language):
    """Tell if all the page content has been updated since the last
    change of the official version (settings.LANGUAGE_CODE)

    This is approximated by comparing the last modified date of any
    content in the page, not comparing each content block to its
    corresponding official language version.  That allows users to
    easily make "do nothing" changes to any content block when no
    change is required for a language.
    """
    lang_code = getattr(settings, 'LANGUAGE_CODE', None)
    if lang_code == language:
        # official version is always "up to date"
        return True
    # get the last modified date for the official version
    last_modified = Content.objects.filter(
        language=lang_code,
        page=page).order_by('-creation_date')
    if not last_modified:
        # no official version
        return True
    lang_modified = Content.objects.filter(
        language=language,
        page=page).order_by('-creation_date')[0].creation_date
    return lang_modified > last_modified[0].creation_date


register.filter(language_content_up_to_date)


@register.assignment_tag
def get_pages_with_tag(tag):
    """
    Return Pages with given tag

    Syntax::

        {% get_pages_with_tag <tag name> as <varname> %}

    Example use::
        {% get_pages_with_tag "footer" as pages %}
    """
    return Page.objects.filter(tags__name__in=[tag])


def do_page_has_content(parser, token):
    """
    Conditional tag that only renders its nodes if the page
    has content for a particular content type. By default the
    current page is used.

    Syntax::

        {% page_has_content <content_type> [<page var name>] %}
            ...
        {%_end page_has_content %}

    Example use::

        {% page_has_content 'header-image' %}
            <img src="{{ MEDIA_URL }}{% imageplaceholder 'header-image' %}">
        {% end_page_has_content %}

    """
    nodelist = parser.parse(('end_page_has_content',))
    parser.delete_first_token()
    args = token.split_contents()
    try:
        content_type = unescape_string_literal(args[1])
    except IndexError:
        raise template.TemplateSyntaxError(
            "%r tag requires the argument content_type" % args[0]
        )
    if len(args) > 2:
        page = args[2]
    else:
        page = None
    return PageHasContentNode(page, content_type, nodelist)


register.tag('page_has_content', do_page_has_content)


class PageHasContentNode(template.Node):

    def __init__(self, page, content_type, nodelist):
        self.page = page or 'current_page'
        self.content_type = content_type
        self.nodelist = nodelist

    def render(self, context):
        page = context.get(self.page)
        if not page:
            return ''
        content = page.get_content(
            context.get('lang', None), self.content_type)
        if(content):
            output = self.nodelist.render(context)
            return output
        return ''
