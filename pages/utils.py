# -*- coding: utf-8 -*-
"""A collection of functions for Page CMS"""
from pages import settings
from pages.cache import cache
from pages.phttp import get_request_mock

from django.conf import settings as django_settings
from django.template import TemplateDoesNotExist
from django.template import loader, Context
from django.core.management.base import CommandError
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

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
        temp = loader.get_template(template_name)
    except TemplateDoesNotExist:
        return []

    plist, blist = [], []
    _placeholders_recursif(temp.nodelist, plist, blist)
    return plist


def _placeholders_recursif(nodelist, plist, blist):
    """Recursively search into a template node list for PlaceholderNode
    node."""
    # I needed to do this lazy import to compile the documentation
    from django.template.loader_tags import BlockNode

    for node in nodelist:

        # extends node?
        if hasattr(node, 'parent_name'):
            _placeholders_recursif(node.get_parent(Context()).nodelist,
                                                        plist, blist)
        # include node?
        elif hasattr(node, 'template'):
            _placeholders_recursif(node.template.nodelist, plist, blist)

        # Is it a placeholder?
        if hasattr(node, 'page') and hasattr(node, 'parsed') and \
                hasattr(node, 'as_varname') and hasattr(node, 'name'):
            already_in_plist = False
            for placeholder in plist:
                if placeholder.name == node.name:
                    already_in_plist = True
            if not already_in_plist:
                if len(blist):
                    node.found_in_block = blist[len(blist) - 1]
                plist.append(node)
            node.render(Context())

        for key in ('nodelist', 'nodelist_true', 'nodelist_false'):
            if isinstance(node, BlockNode):
                # delete placeholders found in a block of the same name
                offset = 0
                _plist = [(i, v) for i, v in enumerate(plist)]
                for index, pl in _plist:
                    if pl.found_in_block and \
                            pl.found_in_block.name == node.name \
                            and pl.found_in_block != node:
                        del plist[index - offset]
                        offset += 1
                blist.append(node)

            if hasattr(node, key):
                try:
                    _placeholders_recursif(getattr(node, key), plist, blist)
                except:
                    pass
            if isinstance(node, BlockNode):
                blist.pop()

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

