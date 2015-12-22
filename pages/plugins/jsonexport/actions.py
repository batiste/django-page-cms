from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponse
from django.db import transaction
from django.shortcuts import render
from django.template import RequestContext

from pages.phttp import get_language_from_request
from pages.plugins.jsonexport.utils import pages_to_json, json_to_pages
from pages.models import Page

JSON_PAGE_EXPORT_FILENAME = 'cms_pages.json'


def export_pages_as_json(modeladmin, request, queryset):
    response = HttpResponse(content_type="application/json")
    response['Content-Disposition'] = 'attachment; filename=%s' % (
        JSON_PAGE_EXPORT_FILENAME,)
    response.write(pages_to_json(queryset))
    return response
export_pages_as_json.short_description = _("Export pages as JSON")


@transaction.atomic
def import_pages_from_json(modeladmin, request, queryset,
        template_name='admin/pages/page/import_pages.html'):

    try:
        j = request.FILES['json']
    except KeyError:
        return render(request, template_name, {
            'nofile': True,
            'app_label': 'pages',
            'opts': Page._meta,
        }, RequestContext(request))

    errors, pages_created = json_to_pages(j.read(), request.user,
        get_language_from_request(request))

    return render(request, template_name, {
        'errors': errors,
        'pages_created': pages_created,
        'app_label': 'pages',
        'opts': Page._meta,
    }, RequestContext(request))

import_pages_from_json.short_description = _("Import some pages from a JSON file")
