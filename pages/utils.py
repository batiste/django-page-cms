# -*- coding: utf-8 -*-
"""A collection of functions for Page CMS"""
import sys, re, logging, pprint, traceback
from django.conf import settings as django_settings
from django.template import TemplateDoesNotExist
from django.template import loader, Context, RequestContext
from django.http import Http404
from django.core.cache import cache
from pages import settings
from pages.http import get_request_mock, get_language_from_request

def get_context_mock():
    """return a mockup dictionnary to use in get_placeholders."""
    context = {'current_page':None}
    if settings.PAGE_EXTRA_CONTEXT:
        context.update(settings.PAGE_EXTRA_CONTEXT())
    return context

def get_placeholders(template_name):
    """Return a list of PlaceholderNode found in the given template.

    :param template_name: the name of the template file
    """
    try:
        temp = loader.get_template(template_name)
    except TemplateDoesNotExist:
        return []
        
    request = get_request_mock()
    context = get_context_mock()
    # I need to render the template in order to extract
    # placeholder tags
    temp.render(RequestContext(request, context))
    plist, blist = [], []
    _placeholders_recursif(temp.nodelist, plist, blist)
    return plist

def _placeholders_recursif(nodelist, plist, blist):
    """Recursively search into a template node list for PlaceholderNode
    node."""
    # I needed to import make this lazy import to make the doc compile
    from django.template.loader_tags import BlockNode
    
    for node in nodelist:

        # extends node
        if hasattr(node, 'parent_name'):
            _placeholders_recursif(node.get_parent(Context()).nodelist,
                                                        plist, blist)
        # include node
        elif hasattr(node, 'template'):
            _placeholders_recursif(node.template.nodelist, plist, blist)

        # It's a placeholder
        if hasattr(node, 'page') and hasattr(node, 'parsed') and \
                hasattr(node, 'as_varname') and hasattr(node, 'name'):
            already_in_plist = False
            for pl in plist:
                if pl.name == node.name:
                    already_in_plist = True
            if not already_in_plist:
                if len(blist):
                    node.found_in_block = blist[len(blist)-1]
                plist.append(node)
            node.render(Context())

        for key in ('nodelist', 'nodelist_true', 'nodelist_false'):
            if isinstance(node, BlockNode):
                # delete placeholders found in a block of the same name
                for index, pl in enumerate(plist):
                    if pl.found_in_block and \
                            pl.found_in_block.name == node.name \
                            and pl.found_in_block != node:
                        del plist[index]
                blist.append(node)
            
            if hasattr(node, key):
                try:
                    _placeholders_recursif(getattr(node, key), plist, blist)
                except:
                    pass
            if isinstance(node, BlockNode):
                blist.pop()

def has_page_add_permission(request, page=None):
    """Return true if the current user has permission to add a new page.

    :param page: not used
    """
    if not settings.PAGE_PERMISSION:
        return True
    else:
        from pages.models import PagePermission
        permission = PagePermission.objects.get_page_id_list(request.user)
        if permission == "All":
            return True
        # the user has the right to add a page under a page he control
        target = request.GET.get('target', None)
        if target is not None:
            try:
                target = int(target)
                if target in permission:
                    return True
            except:
                pass
    return False


def normalize_url(url):
    """Return a normalized url with trailing and without leading slash.
     
     >>> normalize_url(None)
     '/'
     >>> normalize_url('/')
     '/'
     >>> normalize_url('/foo/bar')
     '/foo/bar'
     >>> normalize_url('foo/bar')
     '/foo/bar'
     >>> normalize_url('/foo/bar/')
     '/foo/bar'
    """
    if not url or len(url)==0:
        return '/'
    if not url.startswith('/'):
        url = '/' + url
    if len(url)>1 and url.endswith('/'):
        url = url[0:len(url)-1]
    return url

PAGE_CLASS_ID_REGEX = re.compile('page_([0-9]+)')

def filter_link(content, page, language, content_type):
    """Transform the HTML link href to point to the targeted page
    absolute URL.

     >>> filter_link('<a class="page_1">hello</a>', page, 'en-us', body)
     '<a href="/pages/page-1" class="page_1">hello</a>'
    """
    if not settings.PAGE_LINK_FILTER:
        return content
    if content_type in ('title', 'slug'):
        return content
    from BeautifulSoup import BeautifulSoup
    tree = BeautifulSoup(content)
    tags = tree.findAll('a')
    if len(tags) == 0:
        return content
    for tag in tags:
        tag_class = tag.get('class', False)
        if tag_class:
            # find page link with class 'page_ID'
            result = PAGE_CLASS_ID_REGEX.search(content)
            if result and result.group:
                try:
                    # TODO: try the cache before fetching the Page object
                    from pages.models import Page
                    target_page = Page.objects.get(pk=int(result.group(1)))
                    tag['href'] = target_page.get_absolute_url(language)
                except Page.DoesNotExist:
                    cache.set(Page.PAGE_BROKEN_LINK_KEY % page.id, True)
                    tag['class'] = 'pagelink_broken'
    return unicode(tree)
