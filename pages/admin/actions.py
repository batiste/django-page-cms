from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponse
from django.utils import simplejson
from django.core.serializers.json import DjangoJSONEncoder

JSON_PAGE_EXPORT_NAME = 'gerbi_cms_page_export_version'
JSON_PAGE_EXPORT_VERSION = 1
JSON_PAGE_EXPORT_FILENAME = 'cms_pages.json'

# make it readable -- there are better ways to save space
JSON_PAGE_EXPORT_INDENT = 2

def export_pages_as_json(modeladmin, request, queryset):
    response = HttpResponse(mimetype="application/json")
    response['Content-Disposition'] = 'attachment; filename=%s' % (
        JSON_PAGE_EXPORT_FILENAME,)
    response.write(simplejson.dumps(
        {JSON_PAGE_EXPORT_NAME: JSON_PAGE_EXPORT_VERSION,
            'pages': [page.dump_json_data() for page in queryset]},
        cls=DjangoJSONEncoder, indent=JSON_PAGE_EXPORT_INDENT))
    return response
export_pages_as_json.short_description = _("Export pages as JSON")
