# -*- coding: utf-8 -*-
from django.conf import settings as django_settings
from django.template import TemplateDoesNotExist
from django.template.loader_tags import ExtendsNode, ConstantIncludeNode
from django.template.loader_tags import BlockNode
from django.template import loader, Context, RequestContext
from django.http import Http404

from pages import settings
from pages.http import get_request_mock, get_language_from_request

def get_placeholders(template_name):
    """
    Return a list of PlaceholderNode found in the given template
    """
    try:
        temp = loader.get_template(template_name)
    except TemplateDoesNotExist:
        return []
        
    request = get_request_mock()

    try:
        # to avoid circular import
        from pages.views import details
        context = details(request, only_context=True)
    except Http404:
        context = {}
    temp.render(RequestContext(request, context))
    plist, blist = [], []
    placeholders_recursif(temp.nodelist, plist, blist)
    return plist

def placeholders_recursif(nodelist, plist, blist):
    """
    Recursively search into a template node list for PlaceholderNode node
    """
    
    for node in nodelist:

        # extends node
        if hasattr(node, 'parent_name'):
            placeholders_recursif(node.get_parent(Context()).nodelist,
                                                        plist, blist)
        # include node
        elif hasattr(node, 'template'):
            placeholders_recursif(node.template.nodelist, plist, blist)

        # It's a placeholder
        if hasattr(node, 'page') and hasattr(node, 'parsed') and \
                hasattr(node, 'as_varname') and hasattr(node, 'name'):
            already_in_plist = False
            for p in plist:
                if p.name == node.name:
                    already_in_plist = True
            if not already_in_plist:
                if len(blist):
                    node.found_in_block = blist[len(blist)-1]
                plist.append(node)
            node.render(Context())

        for key in ('nodelist', 'nodelist_true', 'nodelist_false'):
            if isinstance(node, BlockNode):
                # delete placeholders found in a block of the same name
                for index, p in enumerate(plist):
                    if p.found_in_block and \
                            p.found_in_block.name == node.name \
                            and p.found_in_block != node:
                        del plist[index]
                blist.append(node)
            
            if hasattr(node, key):
                try:
                    placeholders_recursif(getattr(node, key), plist, blist)
                except:
                    pass
            if isinstance(node, BlockNode):
                blist.pop()


def has_page_add_permission(request, page=None):
    """
    Return true if the current user has permission to add a new page.
    """
    if not settings.PAGE_PERMISSION:
        return True
    else:
        from pages.models import PagePermission
        permission = PagePermission.objects.get_page_id_list(request.user)
        if permission == "All":
            return True
    return False

# TODO: move this in the manager
def get_page_from_slug(slug, request, lang=None):
    from pages.models import Content, Page
    from django.core.urlresolvers import reverse
    lang = get_language_from_request(request)
    relative_url = request.path.replace(reverse('pages-root'), '')
    page_ids = Content.objects.get_page_ids_by_slug(slug)
    pages_list = Page.objects.filter(id__in=page_ids)
    current_page = None
    if len(pages_list) == 1:
        return pages_list[0]
    if len(pages_list) > 1:
        for page in pages_list:
            if page.get_url(lang) == relative_url:
                return page
    return None
