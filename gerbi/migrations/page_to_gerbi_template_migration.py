
import difflib

template_tag_changes = [
    ("pages_menu", "gerbi_menu"),
    ("pages_children_menu", "gerbi_children_menu"),
    ("pages_sub_menu", "gerbi_sub_menu"),
    ("pages_siblings_menu", "gerbi_siblings_menu"),
    ("show_content", "gerbi_show_content"),
    ("show_slug_with_level", "gerbi_show_slug_with_level"),
    ("show_absolute_url", "gerbi_show_absolute_url"),
    ("pages_dynamic_tree_menu", "gerbi_dynamic_tree_menu"),
    ("pages_breadcrumb", "gerbi_breadcrumb"),
    ("get_page", "gerbi_get_page"),
    ("get_content", "gerbi_get_content"),
    ("load_pages", "gerbi_load_pages"),
    ("placeholder", "gerbi_placeholder"),
    ("imageplaceholder", "gerbi_image_placeholder"),
    ("fileplaceholder", "gerbi_file_placeholder"),
    ("videoplaceholder", "gerbi_video_placeholder"),
    ("contactplaceholder", "gerbi_contact_placeholder"),
]

template_tag_filter = [
    ("has_content_in", "gerbi_has_content_in"),
    ("language_content_up_to_date", "gerbi_language_content_up_to_date"),
    ("show_revisions", "gerbi_show_revisions"),
]

variable_changes = [
    (" current_page", " gerbi_current_page"),
    ("{{ current_page", "{{ gerbi_current_page"),
    ("pages_navigation", "gerbi_navigation"),
]


def find_tag_use(filename, apply_changes=False):
    file = open(filename, "r")
    template = file.read()
    original = str(template)
    file.close()

    changes = False
    for tag in template_tag_changes:
        search = " %s(" % tag[0]
        index = template.find(search)
        if index > 0:
            replacement = " %s(" % tag[1]
            template = template.replace(search, replacement)
            changes = True

    for tag in variable_changes:
        search = tag[0]
        index = template.find(search)
        if index > 0:
            replacement = tag[1]
            template = template.replace(search, replacement)
            changes = True

    for tag in template_tag_filter:
        search = "|%s" % tag[0]
        index = template.find(search)
        if index > 0:
            replacement = "|%s" % tag[1]
            template = template.replace(search, replacement)
            changes = True

    if apply_changes:
        file = open(filename, "w")
        file.write(template)
        file.close()
        return

    if changes:
        print "-----------------------------------------------"
        print "In file %s" % filename
        print "-----------------------------------------------"
        d = difflib.Differ()
        #print original.split()
        assert original != template
        for line in d.compare(original.splitlines(), template.splitlines()):
            if(line.startswith('+') or line.startswith('-') or line.startswith('?')):
                print line
        print "-----------------------------------------------"
        print ""
    return changes

import os

search_dir = "gerbi/templates/"

for dirname, dirnames, filenames in os.walk(search_dir):
    for filename in filenames:
        if filename.endswith("html"):
            changes_needed = find_tag_use(os.path.join(dirname, filename))
            if changes_needed:
                text = raw_input("Proceed to apply those changes on this file? [Y/n]")
                if len(text) == 0 or text.lower() == 'y':
                    find_tag_use(os.path.join(dirname, filename), apply_changes=True)



