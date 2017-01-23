import pages.admin
from pages.plugins.jsonexport.actions import export_pages_as_json
from pages.plugins.jsonexport.actions import import_pages_from_json
pages.admin.add_page_action(export_pages_as_json)
pages.admin.add_page_action(import_pages_from_json)