from django import template
from django.core.cache import cache
from django.utils.safestring import SafeUnicode, mark_safe
from django.utils.translation import ugettext_lazy as _
from django.template import Template, TemplateSyntaxError
from django.conf import settings as global_settings

from pages import settings
from pages.models import Content, Page
from pages.utils import get_language_from_request

register = template.Library()

PLACEHOLDER_ERROR = _("[Placeholder %(name)s had syntax error: %(error)s]")

def get_page_children_for_site(page, site):
    return page.get_children().filter(sites__domain=site.domain)

def pages_menu(context, page, url='/'):
    """render a nested list of all children of the pages"""
    request = context['request']
    site = request.site
    children = get_page_children_for_site(page, site)
    PAGE_CONTENT_CACHE_DURATION = settings.PAGE_CONTENT_CACHE_DURATION
    lang = get_language_from_request(request)
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
    site = request.site
    children = get_page_children_for_site(page, site)
    if 'current_page' in context:
        current_page = context['current_page']
    return locals()
pages_sub_menu = register.inclusion_tag('pages/sub_menu.html',
                                        takes_context=True)(pages_sub_menu)

def pages_admin_menu(context, page, url='/admin/pages/page/', level=None):
    """Render the admin table of pages"""
    request = context['request']
    site = request.site
    children = get_page_children_for_site(page, site)
    has_permission = page.has_page_permission(request)
    # level is used to add a left margin on table row
    if has_permission:
        if level is None:
            level = 0
        else:
            level = level+3
    return locals()
pages_admin_menu = register.inclusion_tag('admin/pages/page/menu.html',
                                          takes_context=True)(pages_admin_menu)

def has_permission(page, request):
    return page.has_page_permission(request)
register.filter(has_permission)

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
    request = context.get('request', False)
    if not request or not page:
        return {'content':''}
    # if the page is a SafeUnicode, try to use it like a slug
    if isinstance(page, SafeUnicode):
        c = Content.objects.filter(type='slug', body=page)
        if len(c):
            page = c[0].page
        else:
            return {'content':''}
    if lang is None:
        lang = get_language_from_request(context['request'])
    if hasattr(settings, 'PAGE_CONTENT_CACHE_DURATION'):
        key = 'content_cache_pid:'+str(page.id)+'_l:'+str(lang)+'_type:'+str(content_type)
        c = cache.get(key)
        if not c:
            c = Content.objects.get_content(page, lang, content_type, True)
            cache.set(key, c, settings.PAGE_CONTENT_CACHE_DURATION)
    else:
        c = Content.objects.get_content(page, lang, content_type, True)
    if c:
        return {'content':c}
    return {'content':''}
show_content = register.inclusion_tag('pages/content.html',
                                      takes_context=True)(show_content)

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
        c = Content.objects.filter(type='slug', body=page)
        if len(c):
            page = c[0].page
        else:
            page = None
    if not request or not page:
        return {'content':''}
    if lang is None:
        lang = get_language_from_request(context['request'])
    if hasattr(settings, 'PAGE_CONTENT_CACHE_DURATION'):
        key = 'page_url_pid:'+str(page.id)+'_l:'+str(lang)+'_type:absolute_url'
        url = cache.get(key)
        if not url:
            url = page.get_absolute_url(language=lang)
            cache.set(key, url, settings.PAGE_CONTENT_CACHE_DURATION)
    else:
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
        language = get_language_from_request(context['request'])
        request = context['request']
        content = Content.objects.get_content(context[self.page], language,
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
