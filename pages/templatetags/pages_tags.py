# -*- coding: utf-8 -*-
"""Page CMS page_tags template tags"""
from django import template
from django.utils.safestring import SafeUnicode, mark_safe
from django.utils.translation import ugettext_lazy as _
from django.template import Template, TemplateSyntaxError
from django.conf import settings as global_settings
import urllib

from pages import settings
from pages.models import Content, Page
from pages.views import details

register = template.Library()

PLACEHOLDER_ERROR = _("[Placeholder %(name)s had syntax error: %(error)s]")

def _get_content(context, page, content_type, lang, fallback=True):
    """Helper function used by placeholder nodes."""
    if not page:
        return ''

    if not lang and 'lang' in context:
        lang = context.get('lang', settings.PAGE_DEFAULT_LANGUAGE)
    
    # if the page is a SafeUnicode, try to use it like a slug
    if isinstance(page, SafeUnicode) or isinstance(page, unicode):
        page = Page.objects.from_path(page, lang)

    if not page:
        return ''

    c = Content.objects.get_content(page, lang, content_type, fallback)
    return c

"""Filters"""

def has_content_in(page, language):
    """Fitler that return ``True`` if the page has any content in a
    particular language.

    :param page: the current page
    :param language: the language you want to look at
    """
    return Content.objects.filter(page=page, language=language).count() > 0
register.filter(has_content_in)

def has_permission(page, request):
    """Tell if a user has permissions on the page.

    :param page: the current page
    :param request: the request object where the user is extracted
    """
    return page.has_page_permission(request)
register.filter(has_permission)

"""Inclusion tags"""

def pages_menu(context, page, url='/'):
    """Render a nested list of all the descendents of the given page,
    including this page.

    :param page: the page where to start the menu from.
    :param url: not used anymore.
    """
    lang = context.get('lang', settings.PAGE_DEFAULT_LANGUAGE)
    path = context.get('path', None)
    site_id = None
    children = page.get_children_for_frontend()
    if 'current_page' in context:
        current_page = context['current_page']
    return locals()
pages_menu = register.inclusion_tag('pages/menu.html',
                                    takes_context=True)(pages_menu)

def pages_sub_menu(context, page, url='/'):
    """Get the root page of the given page and
    render a nested list of all root's children pages.
    Good for rendering a secondary menu.

    :param page: the page where to start the menu from.
    :param url: not used anymore.
    """
    lang = context.get('lang', settings.PAGE_DEFAULT_LANGUAGE)
    path = context.get('path', None)
    root = page.get_root()
    children = root.get_children_for_frontend()
    if 'current_page' in context:
        current_page = context['current_page']
    return locals()
pages_sub_menu = register.inclusion_tag('pages/sub_menu.html',
                                        takes_context=True)(pages_sub_menu)

def pages_admin_menu(context, page, url='', level=None):
    """Render the admin table of pages."""
    request = context['request']
    
    if "tree_expanded" in request.COOKIES:
        cookie_string = urllib.unquote(request.COOKIES['tree_expanded'])
        if cookie_string:
            ids = [int(id) for id in 
                urllib.unquote(request.COOKIES['tree_expanded']).split(',')]
            if page.id in ids:
                expanded = True
    
    page_languages = settings.PAGE_LANGUAGES
    has_permission = page.has_page_permission(request)
    PAGES_MEDIA_URL = settings.PAGES_MEDIA_URL
    lang = context.get('lang', settings.PAGE_DEFAULT_LANGUAGE)

    return locals()
pages_admin_menu = register.inclusion_tag('admin/pages/page/menu.html',
                                        takes_context=True)(pages_admin_menu)


def show_content(context, page, content_type, lang=None, fallback=True):
    """Display a content type from a page.
    
    Example::

        {% show_content page_object "title" %}
    
    You can also use the slug of a page::
    
        {% show_content "my-page-slug" "title" %}

    :param page: the page object
    :param content_type: content_type used by a placeholder
    :param lang: the wanted language (default None, use the request object to know)
    :param fallback: use fallback content
    """
    return {'content':_get_content(context, page, content_type, lang,
                                                                fallback)}
show_content = register.inclusion_tag('pages/content.html',
                                      takes_context=True)(show_content)

def show_slug_with_level(context, page, lang=None, fallback=True):
    """Display slug with level by language."""
    if not page:
        return ''
    if not lang:
        lang = context.get('lang', settings.PAGE_DEFAULT_LANGUAGE)

    if not page:
        return ''

    return {'content': page.slug_with_level(lang)}
show_slug_with_level = register.inclusion_tag('pages/content.html',
                                      takes_context=True)(show_slug_with_level)


def show_absolute_url(context, page, lang=None):
    """Show the url of a page in the right language

    Example ::
    
        {% show_absolute_url page_object %}

    You can also use the slug of a page::
    
        {% show_absolute_url "my-page-slug" %}

    Keyword arguments:
    :param page: the page object or a slug string
    :param lang: the wanted language (defaults to `settings.PAGE_DEFAULT_LANGUAGE`)
    """
    lang = context.get('lang', settings.PAGE_DEFAULT_LANGUAGE)
    # if the page is a SafeUnicode, try to use it like a slug
    if isinstance(page, SafeUnicode) or isinstance(page, unicode):
        page = Page.objects.from_path(page, lang)
    if not page:
        return {'content':''}
    url = page.get_absolute_url(language=lang)
    if url:
        return {'content':url}
    return {'content':''}
show_absolute_url = register.inclusion_tag('pages/content.html',
                                      takes_context=True)(show_absolute_url)

def show_revisions(context, page, content_type, lang=None):
    """Render the last 10 revisions of a page content with a list using
        the ``pages/revisions.html`` template"""
    if not settings.PAGE_CONTENT_REVISION:
        return {'revisions':None}
    revisions = Content.objects.filter(page=page, language=lang,
                                type=content_type).order_by('-creation_date')
    if len(revisions) < 2:
        return {'revisions':None}
    return {'revisions':revisions[0:10]}
show_revisions = register.inclusion_tag('pages/revisions.html',
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
    request = context['request']
    site_id = None
    children = None
    lang = context.get('lang', settings.PAGE_DEFAULT_LANGUAGE)
    if 'current_page' in context:
        current_page = context['current_page']
        # if this node is expanded, we also have to render its children
        # a node is expanded if it is the current node or one of its ancestors
        if page.lft <= current_page.lft and page.rght >= current_page.rght:
            children = page.get_children_for_frontend()
    return locals()
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
    lang = context.get('lang', settings.PAGE_DEFAULT_LANGUAGE)
    request = context['request']
    site_id = None
    pages = page.get_ancestors()
    return locals()
pages_breadcrumb = register.inclusion_tag(
    'pages/breadcrumb.html',
    takes_context=True
)(pages_breadcrumb)


"""Tags"""

class GetContentNode(template.Node):
    """Get content node"""
    def __init__(self, page, content_type, varname, lang):
        self.page = page
        self.content_type = content_type
        self.varname = varname
        self.lang = lang
    def render(self, context):
        if self.lang is None:
            lang = None
        else:
            lang = self.lang.resolve(context)
        context[self.varname] = _get_content(context,
            self.page.resolve(context),
            self.content_type.resolve(context),
            lang)
        return ''

def do_get_content(parser, token):
    """Store a content type from a page into a context variable.

    Example::
    
        {% get_content page_object "title" as content %}

    You can also use the slug of a page::
    
        {% get_content "my-page-slug" "title" as content %}

    Syntax::
    
        {% get_content page type [lang] as name %}

    :param page: the page object
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
    if len(bits) == 6:
        lang = parser.compile_filter(bits[3])
    return GetContentNode(page, content_type, varname, lang)
do_get_content = register.tag('get_content', do_get_content)


class LoadPagesNode(template.Node):
    """Load page node."""
    def render(self, context):
        if 'pages' not in context:
            pages = Page.objects.navigation().order_by("tree_id")
            context.update({'pages': pages})
        if 'current_page' not in context:
            context.update({'current_page':None})
        return ''

def do_load_pages(parser, token):
    """Load the navigation pages, lang, and current_page variables into the
    current context.

    Example::
    
        <ul>
            {% load_pages %}
            {% for page in pages %}
                {% pages_menu page %}
            {% endfor %}
        </ul>
    """
    return LoadPagesNode()
do_load_pages = register.tag('load_pages', do_load_pages)


class PlaceholderNode(template.Node):
    """This template node is used to output page content and
    also in the admin to dynamically generate input fields.

    :param name: the name of the placeholder you want to show/create
    :param page: the optional page object
    :param widget: the widget you want to use in the admin interface. Take
        a look into :mod:`pages.admin.widgets` to see which widgets
        are available.
    :param parsed: if the ``parsed`` word is given, the content of the
        placeholder is evaluated as template code, within the current context.
    :param as_varname: if ``as_varname`` is defined, no value will be returned.
        A variable will be created in the context with the defined name.
    """
    def handle_token(cls, parser, token):
        """
        Method that parse the template tag syntax following this syntax::

            {% placeholder <name> [on <page>] [with <widget>] \
[parsed] [as <varname>] %}
        """
        bits = token.split_contents()
        count = len(bits)
        error_string = '%r tag requires at least one argument' % bits[0]
        if count <= 1:
            raise template.TemplateSyntaxError(error_string)
        name = bits[1]
        remaining = bits[2:]
        params = {}
        while remaining:
            bit = remaining[0]
            if bit not in ('as', 'on', 'with', 'parsed'):
                raise template.TemplateSyntaxError(
                    "%r is not an correct option for a placeholder" % bit)
            if bit in ('as', 'on', 'with'):
                if len(remaining) < 2:
                    raise template.TemplateSyntaxError(
                    "Placeholder option '%s' need a parameter" % bit)
                if bit == 'as':
                    params['as_varname'] = remaining[1]
                if bit == 'with':
                    params['widget'] = remaining[1]
                if bit == 'on':
                    params['page'] = remaining[1]
                remaining = remaining[2:]
            else:
                params['parsed'] = True
                remaining = remaining[1:]
        return cls(name, **params)
    handle_token = classmethod(handle_token)
    
    def __init__(self, name, page=None, widget=None, parsed=False, as_varname=None):
        self.page = page or 'current_page'
        self.name = name
        self.widget = widget
        self.parsed = parsed
        self.as_varname = as_varname
        self.found_in_block = None

    def render(self, context):
        if not self.page in context:
            return ''
        # current_page can be set to None
        if not context[self.page]:
            return ''

        lang = context.get('lang', settings.PAGE_DEFAULT_LANGUAGE)
        content = Content.objects.get_content(context[self.page], lang,
                                              self.name, True)
        if not content:
            return ''
        if self.parsed:
            try:
                t = template.Template(content, name=self.name)
                content = mark_safe(t.render(context))
            except template.TemplateSyntaxError, error:
                if global_settings.DEBUG:
                    error = PLACEHOLDER_ERROR % {
                        'name': self.name,
                        'error': error,
                    }
                    if self.as_varname is None:
                        return error
                    context[self.as_varname] = error
                    return ''
                else:
                    return ''
        if self.as_varname is None:
            return content
        context[self.as_varname] = content
        return ''

    def __repr__(self):
        return "<Placeholder Node: %s>" % self.name

def do_placeholder(parser, token):
    """
    Syntax::

        {% placeholder [name] %}
        {% placeholder [name] parsed %}

        {% placeholder [name] on [page]  %}
        {% placeholder [name] with [widget] %}
        {% placeholder [name] on [page] with [widget] %}

        {% placeholder [name] on [page] parsed %}
        {% placeholder [name] with [widget] parsed %}
        {% placeholder [name] on [page] with [widget] parsed %}

    Example usage::

        {% placeholder about %}
        {% placeholder body with TextArea as body_text %}
        {% placeholder welcome with TextArea parsed as welcome_text %}
        {% placeholder teaser on next_page with TextArea parsed %}
    """
    return PlaceholderNode.handle_token(parser, token)

register.tag('placeholder', do_placeholder)


