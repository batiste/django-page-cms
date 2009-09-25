# -*- coding: utf-8 -*-
"""A collection of functions for Page CMS"""
import sys, re, logging, pprint, traceback
from django.conf import settings as django_settings
from django.template import TemplateDoesNotExist
from django.template import loader, Context, RequestContext
from django.http import Http404
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

def mark_deleted(content):
    body = BeautifulSoup(content)
    tags = body.findAll('a')
    broken_links = 0
    for tag in tags:
        if tag.string and tag.string.strip():
            if tag.get('class', ''):
                # find link(s) with the page_id > set link to broken
                if 'page_'+str(self.id) in tag['class']:
                    obj_pagelink_broken += 1
                    tag.replaceWith('<a class="pagelink_broken" title="' \
                        + self.title(language) 
                        + '"href="'+self.get_absolute_url(language) + '">'
                        + tag.string.strip() + '</a>')
                # count already broken page link(s)
                if 'pagelink_broken' in tag['class']:
                    broken_links += 1
    return unicode(body), broken_links
