# -*- coding: utf-8 -*-
"""A collection of functions for Page CMS"""
from pages import settings
from pages.cache import cache
from pages.phttp import get_request_mock

from django.conf import settings as django_settings
from django.core.management.base import CommandError
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.template import Context
from django import template

import re
from datetime import datetime

def get_now():
    if django_settings.USE_TZ:
        return datetime.utcnow().replace(tzinfo=timezone.utc)
    else:
        return datetime.now()

def get_placeholders(template_name):
    """Return a list of PlaceholderNode found in the given template.

    :param template_name: the name of the template file
    """
    try:
        temp_wrapper = template.loader.get_template(template_name)
    except template.TemplateDoesNotExist:
        return []

    plist, blist = [], []
    temp = temp_wrapper.template
    _placeholders_recursif(temp.nodelist, plist, blist)

    previous = {}
    block_to_remove = []
    for block in blist:
        if block.name in previous:
            if not hasattr(block, 'has_super_var'):
                block_to_remove.append(previous[block.name])
        previous[block.name] = block

    def keep(p):
        return not p.found_in_block in block_to_remove

    placeholders = [p for p in plist if keep(p)]
    names = []
    pfiltered = []
    for p in placeholders:
        if p.ctype not in names:
            pfiltered.append(p)
            names.append(p.ctype)

    return pfiltered


dummy_context = Context()
dummy_context.template = template.Template("")

def _placeholders_recursif(nodelist, plist, blist):
    """Recursively search into a template node list for PlaceholderNode
    node."""
    # I needed to do this lazy import to compile the documentation
    from django.template.loader_tags import BlockNode

    if len(blist):
        block = blist[-1]
    else:
        block = None

    for node in nodelist:

        if isinstance(node, BlockNode):
            if node not in blist:
                blist.append(node)
            if not block:
                block = node

        if block:
            if isinstance(node, template.base.VariableNode):
                if(node.filter_expression.var.var == u'block.super'):
                    block.has_super_var = True

        # extends node?
        if hasattr(node, 'parent_name'):
            _placeholders_recursif(node.get_parent(dummy_context).nodelist,
                                                        plist, blist)
        # include node?
        elif hasattr(node, 'template') and hasattr(node.template, 'nodelist'):
            _placeholders_recursif(node.template.nodelist, plist, blist)

        # Is it a placeholder?
        if hasattr(node, 'page') and hasattr(node, 'parsed') and \
            hasattr(node, 'as_varname') and hasattr(node, 'name'):
            if block:
                node.found_in_block = block
            plist.append(node)
            node.render(dummy_context)

        for key in ('nodelist', 'nodelist_true', 'nodelist_false'):

            if hasattr(node, key):
                try:
                    _placeholders_recursif(getattr(node, key), plist, blist)
                except:
                    pass



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
    if not url or len(url) == 0:
        return '/'
    if not url.startswith('/'):
        url = '/' + url
    if len(url) > 1 and url.endswith('/'):
        url = url[0:len(url) - 1]
    return url

