
import difflib

template_tag_changes = [
    ("has_content_in", "gerbi_has_content_in"),
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

variable_changes = [
    ("current_page", "gerbi_current_page"),
    ("pages_navigation", "gerbi_navigation"),
]


def find_tag_use(filename):
    file = open(filename, "r")
    template = file.read()
    original = str(template)
    file.close()

    changes = False
    for tag in template_tag_changes:
        search = "{%% %s" % tag[0]
        index = template.find(search)
        if index > 0:
            replacement = "{%% %s" % tag[1]
            template = template.replace(search, replacement)
            changes = True

    for tag in variable_changes:
        search = tag[0]
        index = template.find(search)
        if index > 0:
            replacement = tag[1]
            template = template.replace(search, replacement)
            changes = True

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

import os

search_dir = "gerbi/templates"

for dirname, dirnames, filenames in os.walk(search_dir):
    for filename in filenames:
        find_tag_use(os.path.join(dirname, filename))


