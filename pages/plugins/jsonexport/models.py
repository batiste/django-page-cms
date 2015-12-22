import pages.admin
from pages.plugins.jsonexport.actions import export_pages_as_json
from pages.plugins.jsonexport.actions import import_pages_from_json
pages.admin.PageAdmin.add_action(export_pages_as_json)
pages.admin.PageAdmin.add_action(import_pages_from_json)