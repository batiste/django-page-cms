from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponse
from django.conf import settings as global_settings
from django.db import transaction
from django.shortcuts import redirect, render_to_response
from django.template import RequestContext

from pages import settings
from pages.http import get_language_from_request
from pages.utils import get_placeholders, pages_to_json, json_to_pages
from pages.models import Page

JSON_PAGE_EXPORT_FILENAME = 'cms_pages.json'


def export_pages_as_json(modeladmin, request, queryset):
    response = HttpResponse(mimetype="application/json")
    response['Content-Disposition'] = 'attachment; filename=%s' % (
        JSON_PAGE_EXPORT_FILENAME,)
    response.write(pages_to_json(queryset))
    return response
export_pages_as_json.short_description = _("Export pages as JSON")

@transaction.commit_on_success
def import_pages_from_json(request,
        template_name='admin/pages/page/import_pages.html'):
    try:
        j = request.FILES['json']
    except KeyError:
        return redirect('admin:page-index')

    errors, pages_created = json_to_pages(j.read(), request.user,
        get_language_from_request(request))

    return render_to_response(template_name, {
        'errors': errors,
        'pages_created': pages_created,
        'app_label': 'pages',
        'opts': Page._meta,
    }, RequestContext(request))

