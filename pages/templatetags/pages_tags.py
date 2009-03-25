# -*- coding: utf-8 -*-
from django import template
from django.utils.safestring import SafeUnicode, mark_safe
from django.utils.translation import ugettext_lazy as _
from django.template import Template, TemplateSyntaxError
from django.conf import settings as global_settings
import urllib

from pages import settings
from pages.models import Content, Page
from pages.utils import get_language_from_request

register = template.Library()

PLACEHOLDER_ERROR = _("[Placeholder %(name)s had syntax error: %(error)s]")

def pages_menu(context, page, url='/'):
    """render a nested list of all children of the pages"""
    request = context['request']
    site_id = None
    children = page.get_children_for_frontend()
    PAGE_CONTENT_CACHE_DURATION = settings.PAGE_CONTENT_CACHE_DURATION
    if 'current_page' in context:
        current_page = context['current_page']
    return locals()
pages_menu = register.inclusion_tag('pages/menu.html',
                                    takes_context=True)(pages_menu)

def pages_sub_menu(context, page, url='/'):
    """Get the root page of the current page and 
    render a nested list of all root's children pages"""
    root = page.get_root()
    request = context['request']
    children = page.get_children_for_frontend()
    if 'current_page' in context:
        current_page = context['current_page']
    return locals()
pages_sub_menu = register.inclusion_tag('pages/sub_menu.html',
                                        takes_context=True)(pages_sub_menu)

def pages_admin_menu(context, page, url='/admin/pages/page/', level=None):
    """Render the admin table of pages"""
    request = context['request']
    
    if "tree_expanded" in request.COOKIES:
        cookie_string = urllib.unquote(request.COOKIES['tree_expanded'])
        if cookie_string:
            ids = [int(id) for id in urllib.unquote(request.COOKIES['tree_expanded']).split(',')]
            if page.id in ids:
                expanded = True
    
    has_permission = page.has_page_permission(request)

    return locals()
pages_admin_menu = register.inclusion_tag('admin/pages/page/menu.html',
                                          takes_context=True)(pages_admin_menu)

def has_permission(page, request):
    return page.has_page_permission(request)
register.filter(has_permission)

def get_content(context, page, content_type, lang):
    request = context.get('request', False)
    if not request or not page:
        return ''
    if lang is None:
        if 'lang' in context:
            lang = context['lang']
        else:
            lang = get_language_from_request(context['request'], page)

    # if the page is a SafeUnicode, try to use it like a slug
    if isinstance(page, SafeUnicode):
        c = Content.objects.filter(type='slug', lang=lang, body=page)
        if len(c):
            page = c[0].page
        else:
            ''
    c = Content.objects.get_content(page, lang, content_type, True)
    if c:
        return c
    return ''

def show_content(context, page, content_type, lang=None):
    """Display a content type from a page.
    
    eg: {% show_content page_object "title" %}
    
    You can also use the slug of a page
    
    eg: {% show_content "my-page-slug" "title" %}
    
    Keyword arguments:
    page -- the page object
    args -- content_type used by a placeholder
    lang -- the wanted language (default None, use the request object to know)
    """
    return {'content':get_content(context, page, content_type, lang)}
show_content = register.inclusion_tag('pages/content.html',
                                      takes_context=True)(show_content)

class GetContentNode(template.Node):
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
        context[self.varname] = get_content(context,
            self.page.resolve(context),
            self.content_type.resolve(context),
            lang)
        return ''

def do_get_content(parser, token):
    """Store a content type from a page into a context variable.

    eg: {% get_content page_object "title" as content %}

    You can also use the slug of a page

    eg: {% get_content "my-page-slug" "title" as content %}

    Syntax: {% get_content page type [lang] as name %}
    Arguments:
    page -- the page object
    type -- content_type used by a placeholder
    name -- name of the context variable to store the content in
    lang -- the wanted language (default None, use the request object to know)
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
 

def show_absolute_url(context, page, lang=None):
    """Show the url of a page in the right language
    
    eg: {% show_absolute_url page_object %}
    
    You can also use the slug of a page
    
    eg: {% show_absolute_url "my-page-slug" %}
    
    Keyword arguments:
    page -- the page object or a slug string
    lang -- the wanted language (defaults to None, uses request object else)
    """
    request = context.get('request', False)
    # if the page is a SafeUnicode, try to use it like a slug
    if isinstance(page, SafeUnicode):
        page = get_page_from_slug(slug, request)
    if not request or not page:
        return {'content':''}
    if lang is None:
        if 'lang' in context:
            lang = context['lang']
        else:
            lang = get_language_from_request(context['request'], page)
    url = page.get_absolute_url(language=lang)
    if url:
        return {'content':url}
    return {'content':''}
show_absolute_url = register.inclusion_tag('pages/content.html',
                                      takes_context=True)(show_absolute_url)

def show_revisions(context, page, content_type, lang=None):
    """Render the last 10 revisions of a page content with a list"""
    if not settings.PAGE_CONTENT_REVISION:
        return {'revisions':None}
    revisions = Content.objects.filter(page=page, language=lang,
                                type=content_type).order_by('-creation_date')
    if len(revisions) < 2:
        return {'revisions':None}
    return {'revisions':revisions[0:10]}
show_revisions = register.inclusion_tag('pages/revisions.html',
                                        takes_context=True)(show_revisions)

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

class PlaceholderNode(template.Node):
    """This template node is used to output page content and
    is also used in the admin to dynamically generate input fields.

    Keyword arguments:
    name -- the name of the placeholder you want to show/create
    page -- The optional page object  
    widget -- the widget you want to use in the admin interface. Take
        a look into pages.admin.widgets to see which widgets are available.
    parsed -- If the "parsed" word is given, the content of the
        placeholder is evaluated as template code, within the current context.
    """
    def handle_token(cls, parser, token):
        bits = token.split_contents()
        count = len(bits)
        error_string = '%r tag requires at least one argument' % bits[0]
        if count <= 1:
            raise template.TemplateSyntaxError(error_string)
        if count == 2:
            # {% placeholder [name] %}
            return cls(bits[1])
        if bits[2] not in ('as', 'on', 'with', 'parsed'):
            raise template.TemplateSyntaxError(
                "%r got wrong arguments" % bits[0])
        if count in (3, 4, 5):
            if bits[2] == 'parsed':
                if count == 3:
                    # {% placeholder [name] parsed %}
                    return cls(
                        bits[1],
                        parsed=True,
                    )
                elif count == 5 and bits[3] == 'as':
                    # {% placeholder [name] parsed as [varname] %}
                    return cls(
                        bits[1],
                        as_varname=bits[4],
                        parsed=True,
                    )
            elif bits[2] == 'as':
                # {% placeholder [name] as [varname] %}
                return cls(
                    bits[1],
                    as_varname=bits[3],
                )
            elif bits[2] == 'on':
                # {% placeholder [name] on [page] %}
                return cls(
                    bits[1],
                    page=bits[3],
                )
            elif bits[2] == 'with':
                # {% placeholder [name] with [widget] %}
                return cls(
                    bits[1],
                    widget=bits[3],
                )
        elif count in (6, 7):
            if bits[2] == 'on':
                if bits[4] == 'with':
                    # {% placeholder [name] on [page] with [widget] %}
                    # {% placeholder [name] on [page] with [widget] parsed %}
                    parsed = bits[-1]=='parsed'
                    return cls(
                        bits[1],
                        page=bits[3],
                        widget=bits[5],
                        parsed=parsed,
                    )
                elif bits[4] == 'as':
                    # {% placeholder [name] on [page] as [varname] %}
                    return cls(
                        bits[1],
                        page=bits[3],
                        as_varname=bits[5],
                    )
            elif bits[2] == 'with':
                # {% placeholder [name] with [widget] as [varname] %}
                if bits[4] == 'as':
                    return cls(
                        bits[1],
                        widget=bits[3],
                        as_varname=bits[5],
                    )
                # {% placeholder [name] with [widget] parsed as [varname] %}
                elif bits[4] == 'parsed':
                    return cls(
                        bits[1],
                        widget=bits[3],
                        as_varname=bits[6],
                        parsed=True,
                    )
        elif count == 9:
            # {% placeholder [name] on [page] with [widget] parsed as [varname] %}
            return cls(
                bits[1],
                page=bits[3],
                widget=bits[5],
                as_varname=bits[8],
                parsed=True,
            )
        raise template.TemplateSyntaxError(error_string)
    handle_token = classmethod(handle_token)
    
    def __init__(self, name, page=None, widget=None, parsed=False, as_varname=None):
        self.page = page or 'current_page'
        self.name = name
        self.widget = widget
        self.parsed = parsed
        self.as_varname = as_varname

    def render(self, context):
        if not 'request' in context or not self.page in context:
            return ''

        if 'lang' in context:
            lang = context['lang']
        else:
            lang = get_language_from_request(context['request'], context[self.page])
        request = context['request']
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

register.tag('placeholder', do_placeholder)
