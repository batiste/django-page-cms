# -*- coding: utf-8 -*-
"""A collection of functions for Page CMS"""
from pages import settings
from pages.http import get_request_mock

from django.template import TemplateDoesNotExist
from django.template import loader, Context, RequestContext
from django.core.cache import cache

import re


def get_context_mock():
    """return a mockup dictionnary to use in get_placeholders."""
    context = {'current_page': None}
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
    # I needed to make this lazy import to compile the documentation
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

do_not_msg = "DO NOT MODIFIY BELOW THIS LINE"
po_comment = """Page %s
%s
placeholder=%s
page_id=%d
content_id=%s"""


def export_po_files(path='poexport', stdout=None):
    """
    Export all the content from the published pages into
    po files. The files will be automatically updated
    with the new content if you run the command again.
    """
    if stdout is None:
        import sys
        stdout = sys.stdout
    if not path.endswith('/'):
        path += '/'
    import polib
    import os
    from pages.models import Page, Content
    source_language = settings.PAGE_DEFAULT_LANGUAGE
    source_list = []
    for page in Page.objects.published():
        source_list.extend(page.content_by_language(source_language))

    for lang in settings.PAGE_LANGUAGES:
        if lang[0] != settings.PAGE_DEFAULT_LANGUAGE:
            try:
                os.mkdir(path)
            except OSError:
                pass
            po_path = path + lang[0] + '.po'
            stdout.write("Export language %s.\n" % lang[0])
            po = polib.pofile(po_path)
            po.metadata['Content-Type'] = 'text/plain; charset=utf-8'

            for source_content in source_list:
                page = source_content.page
                try:
                    target_content = Content.objects.get_content_object(
                        page, lang[0], source_content.type)
                    msgstr = target_content.body
                except Content.DoesNotExist:
                    target_content = None
                    msgstr = ""
                if source_content.body:
                    if target_content:
                        tc_id = str(target_content.id)
                    else:
                        tc_id = ""
                    entry = polib.POEntry(msgid=source_content.body,
                        msgstr=msgstr)
                    entry.tcomment = po_comment % (page.title(), do_not_msg,
                        source_content.type, page.id, tc_id)
                    if entry not in po:
                        po.append(entry)
            po.save(po_path)
    stdout.write("""Export finished. The files are available """
        """in the %s directory.\n""" % path)


def import_po_files(path='poexport', stdout=None):
    """
    Import all the content updates from the po files into
    the pages.
    """
    import polib
    import os
    from pages.models import Page, Content
    source_language = settings.PAGE_DEFAULT_LANGUAGE
    source_list = []
    pages_to_invalidate = []
    for page in Page.objects.published():
        source_list.extend(page.content_by_language(source_language))
    if stdout is None:
        import sys
        stdout = sys.stdout
    if not path.endswith('/'):
        path += '/'

    for lang in settings.PAGE_LANGUAGES:
        if lang[0] != settings.PAGE_DEFAULT_LANGUAGE:
            stdout.write("Update language %s.\n" % lang[0])
            po_path = path + lang[0] + '.po'
            po = polib.pofile(po_path)
            for entry in po:
                meta_data = entry.tcomment.split(do_not_msg)[1].split("\n")
                placeholder_name = meta_data[1].split('=')[1]
                page_id = int(meta_data[2].split('=')[1])
                try:
                    content_id = int(meta_data[3].split('=')[1])
                except ValueError:
                    content_id = None

                page = Page.objects.get(id=page_id)
                current_content = Content.objects.get_content(page, lang[0],
                    placeholder_name)
                if current_content != entry.msgstr:
                    stdout.write("Update page %d placeholder %s.\n" % (page_id,
                        placeholder_name))
                    Content.objects.create_content_if_changed(
                        page, lang[0], placeholder_name, entry.msgstr)
                    if page not in pages_to_invalidate:
                        pages_to_invalidate.append(page)

    for page in pages_to_invalidate:
        page.invalidate()
    stdout.write("Import finished from %s.\n" % path)


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
                    tag['href'] = target_page.get_url_path(language)
                except Page.DoesNotExist:
                    cache.set(Page.PAGE_BROKEN_LINK_KEY % page.id, True)
                    tag['class'] = 'pagelink_broken'
    return unicode(tree)
