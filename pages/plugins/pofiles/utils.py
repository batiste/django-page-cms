import polib
import os
from pages.models import Page, Content
import sys
from pages import settings

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
        stdout = sys.stdout
    if not path.endswith('/'):
        path += '/'
    
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
    source_language = settings.PAGE_DEFAULT_LANGUAGE
    source_list = []
    pages_to_invalidate = []
    for page in Page.objects.published():
        source_list.extend(page.content_by_language(source_language))
    if stdout is None:
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