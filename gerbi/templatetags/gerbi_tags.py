"""Gerbi CMS template tags"""
from django import template
from django.utils.safestring import SafeUnicode
from django.template import TemplateSyntaxError
#from django.forms import Widget, Textarea, ImageField, CharField
import urllib
from django.conf import settings

from gerbi import settings as gerbi_settings
from gerbi.models import Content, Page
from gerbi.placeholders import PlaceholderNode, ImagePlaceholderNode, FilePlaceholderNode
from gerbi.placeholders import VideoPlaceholderNode, ContactPlaceholderNode
from gerbi.placeholders import parse_placeholder

register = template.Library()

def get_page_from_string_or_id( context,page_string, lang=None):
    """Return a Page object from a slug or an id."""
    current_page = context.get('gerbi_current_page', None)
    model = Page
    if current_page:
        model = current_page.__class__
        print "s_or_id %s, %s" % ( model, current_page )
    else:
        print "Warning: get_page_from_string_or_id(): context has no current page !"
        
    if type(page_string) == int:
        return model.objects.get(pk=int(page_string))
    # if we have a string coming from some templates templates
    if (isinstance(page_string, SafeUnicode) or
        isinstance(page_string, unicode)):
        if page_string.isdigit():
            return model.objects.get(pk=int(page_string))
        return model.objects.from_path(page_string, lang)
    # in any other case we return the input becasue it's probably
    # a Page object.
    return page_string


def _get_content(context, page, content_type, lang, fallback=True):
    """Helper function used by ``PlaceholderNode``."""
    if not page:
        return ''

    if not lang and 'lang' in context:
        lang = context.get('lang', gerbi_settings.GERBI_DEFAULT_LANGUAGE)
    print "_get_content(): lang is now: %s" % lang
    page = get_page_from_string_or_id( context, page, lang)

    if not page:
        return ''

    content = Content.objects.get_content(page, lang, content_type, fallback)
    return content

"""Filters"""


def gerbi_has_content_in(page, language):
    """Fitler that return ``True`` if the page has any content in a
    particular language.

    :param page: the current page
    :param language: the language you want to look at
    """
    if not page:
        return False
    return len(page.get_languages()) > 0
register.filter(gerbi_has_content_in)


"""Inclusion tags"""

def gerbi_show_absolute_url(context, page, lang=None):
    """Show the url of a page in the right language

    Example ::

        {% gerbi_show_absolute_url page_object %}

    You can also use the slug of a page::

        {% gerbi_show_absolute_url "my-page-slug" %}

    Keyword arguments:
    :param page: the page object, slug or id
    :param lang: the wanted language
        (defaults to `settings.PAGE_DEFAULT_LANGUAGE`)
    """
    if not lang:
        lang = context.get('lang', gerbi_settings.GERBI_DEFAULT_LANGUAGE)
    page = get_page_from_string_or_id( context, page, lang )
    if not page:
        return {'content': ''}
    url = page.get_url_path(language=lang)
    if url:
        return {'content': url}
    return {'content': ''}
gerbi_show_absolute_url = register.inclusion_tag('gerbi/content.html',
                                      takes_context=True)(gerbi_show_absolute_url)


def gerbi_menu(context, page, url='/'):
    """Render a nested list of all the descendents of the given page,
    including this page.

    :param page: the page where to start the menu from.
    :param url: not used anymore.
    """
    lang = context.get('lang', gerbi_settings.GERBI_DEFAULT_LANGUAGE)
    page = get_page_from_string_or_id( context, page, lang)
    if page:
        children = page.get_children_for_frontend()
        context.update({'children': children, 'page': page})
    return context

gerbi_menu = register.inclusion_tag('gerbi/menu.html',
				    takes_context=True)(gerbi_menu)


def gerbi_children_menu(context, page, url='/'):
    """Get the direct children of the given page and render them as a
    list.

    Unlike the gerbi_menu tag, this tag does not display the children's
    children and so on, but only the direct children of the given page.

    :param page: the page where to start the menu from.
    :param url: not used anymore.
    """
    lang = context.get('lang', gerbi_settings.GERBI_DEFAULT_LANGUAGE)
    page = get_page_from_string_or_id( context, page, lang)
    print "gerbi_children_menu(): page is %s" % page
    if page:
        children = page.get_children_for_frontend()
        context.update({'children': children, 'page': page})
    return context

gerbi_children_menu = register.inclusion_tag('gerbi/sub_menu.html',
                                             takes_context=True)(gerbi_children_menu)


def gerbi_sub_menu(context, page, url='/'):
    """Get the root page of the given page and
    render a nested list of all root's children pages.
    Good for rendering a secondary menu.

    :param page: the page where to start the menu from.
    :param url: not used anymore.
    """
    lang = context.get('lang', gerbi_settings.GERBI_DEFAULT_LANGUAGE)
    page = get_page_from_string_or_id( context, page, lang)
    if page:
        root = page.get_root()
        children = root.get_children_for_frontend()
        context.update({'children': children, 'page': page})
    return context

gerbi_sub_menu = register.inclusion_tag('gerbi/sub_menu.html',
                                        takes_context=True)(gerbi_sub_menu)



def gerbi_siblings_menu(context, page, url='/'):
    """Get the parent page of the given page and render a nested list of its
    child pages. Good for rendering a secondary menu.

    :param page: the page where to start the menu from.
    :param url: not used anymore.
    """
    lang = context.get('lang', gerbi_settings.GERBI_DEFAULT_LANGUAGE)
    page = get_page_from_string_or_id( context,page, lang)
    if page:
        if page.parent:
            root = page.parent
        else:
            root = page
        children = root.get_children_for_frontend()
        context.update({'children': children, 'page': page})
    return context

gerbi_siblings_menu = register.inclusion_tag('gerbi/sub_menu.html',
                                    takes_context=True)(gerbi_siblings_menu)


def gerbi_show_content(context, page, content_type, lang=None, fallback=True):
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
    return {'content': _get_content(context, page, content_type, lang,
                                                                fallback)}
gerbi_show_content = register.inclusion_tag('gerbi/content.html',
                                      takes_context=True)(gerbi_show_content)


def gerbi_dynamic_tree_menu(context, page, url='/'):
    """
    Render a "dynamic" tree menu, with all nodes expanded which are either
    ancestors or the current page itself.

    Override ``gerbi/dynamic_tree_menu.html`` if you want to change the
    design.

    :param page: the current page
    :param url: not used anymore
    """
    lang = context.get('lang', gerbi_settings.GERBI_DEFAULT_LANGUAGE)
    page = get_page_from_string_or_id( context, page, lang)
    children = None
    if page and 'gerbi_current_page' in context:
        gerbi_current_page = context['gerbi_current_page']
        # if this node is expanded, we also have to render its children
        # a node is expanded if it is the current node or one of its ancestors
        if(page.tree_id == gerbi_current_page.tree_id and
            page.lft <= gerbi_current_page.lft and
            page.rght >= gerbi_current_page.rght):
            children = page.get_children_for_frontend()
    context.update({'children': children, 'page': page})
    return context

gerbi_dynamic_tree_menu = register.inclusion_tag(
    'gerbi/dynamic_tree_menu.html',
    takes_context=True)(gerbi_dynamic_tree_menu)


def gerbi_breadcrumb(context, page, url='/'):
    """
    Render a breadcrumb like menu.

    Override ``gerbi/breadcrumb.html`` if you want to change the
    design.

    :param page: the current page
    :param url: not used anymore
    """
    lang = context.get('lang', gerbi_settings.GERBI_DEFAULT_LANGUAGE)
    page = get_page_from_string_or_id( context, page, lang)
    pages_navigation = None
    if page:
        gerbi_navigation = page.get_ancestors()
    context.update({'gerbi_navigation': gerbi_navigation, 'page': page})
    return context

gerbi_breadcrumb = register.inclusion_tag(
    'gerbi/breadcrumb.html',
    takes_context=True)(gerbi_breadcrumb)


"""Tags"""


class FakeCSRFNode(template.Node):
    """Fake CSRF node for django 1.1.1"""
    def render(self, context):
        return ''


def do_csrf_token(parser, token):
    return FakeCSRFNode()
try:
    from django.views.decorators.csrf import csrf_protect
except ImportError:
    register.tag('csrf_token', do_csrf_token)


class GetPageNode(template.Node):
    """get_page Node"""
    def __init__(self, page_filter, varname):
        self.page_filter = page_filter
        self.varname = varname

    def render(self, context):
        page_or_id = self.page_filter.resolve(context)
        page = get_page_from_string_or_id( context, page_or_id)
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
register.tag('gerbi_get_page', do_get_page)


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
register.tag('gerbi_get_content', do_get_content)


class LoadPagesNode(template.Node):
    """Load page node."""
    def render(self, context):
        if 'gerbi_current_page' not in context:
            context.update({'gerbi_current_page': None})
            print "Warning: LoadPagesNode::render(): context has no current page !"
            model = Page
        else:
            model = context['gerbi_current_page'].__class__
        if 'pages_navigation' not in context:
            page_set = model.objects.navigation().order_by("tree_id")
            context.update({'pages_navigation': page_set})
        return ''


def do_gerbi_load(parser, token):
    """Load the gerbi_navigation, and gerbi_current_page variables into the
    current context.

    Example::

        <ul>
            {% gerbi_load %}
            {% for page in gerbi_navigation %}
                {% gerbi_menu page %}
            {% endfor %}
        </ul>
    """
    return LoadPagesNode()
register.tag('gerbi_load_pages', do_gerbi_load)


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
register.tag('gerbi_placeholder', do_placeholder)


def do_image_placeholder(parser, token):
    """
    Method that parse the imageplaceholder template tag.
    """
    name, params = parse_placeholder(parser, token)
    return ImagePlaceholderNode(name, **params)
register.tag('gerbi_image_placeholder', do_image_placeholder)

def do_fileplaceholder(parser, token):
    """
    Method that parse the fileplaceholder template tag.
    """
    name, params = parse_placeholder(parser, token)
    return FilePlaceholderNode(name, **params)
register.tag('gerbi_file_placeholder', do_fileplaceholder)

def do_video_placeholder(parser, token):
    """
    Method that parse the imageplaceholder template tag.
    """
    name, params = parse_placeholder(parser, token)
    return VideoPlaceholderNode(name, **params)
register.tag('gerbi_video_placeholder', do_video_placeholder)

def do_contact_placeholder(parser, token):
    """
    Method that parse the contactplaceholder template tag.
    """
    name, params = parse_placeholder(parser, token)
    return ContactPlaceholderNode(name, **params)
register.tag('gerbi_contact_placeholder', do_contact_placeholder)





