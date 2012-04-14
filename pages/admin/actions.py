from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponse
from django.utils import simplejson
from django.conf import settings as global_settings
from django.db import transaction
from django.shortcuts import redirect, render_to_response
from django.template import RequestContext

from pages import settings
from pages.http import get_language_from_request
from pages.utils import get_placeholders
from pages.models import Page

JSON_PAGE_EXPORT_NAME = 'gerbi_cms_page_export_version'
JSON_PAGE_EXPORT_VERSION = 4
JSON_PAGE_EXPORT_FILENAME = 'cms_pages.json'

# make it readable -- there are better ways to save space
JSON_PAGE_EXPORT_INDENT = 2

def export_pages_as_json(modeladmin, request, queryset):
    response = HttpResponse(mimetype="application/json")
    response['Content-Disposition'] = 'attachment; filename=%s' % (
        JSON_PAGE_EXPORT_FILENAME,)
    # selection may be in the wrong order
    queryset = queryset.order_by('tree_id', 'lft')
    response.write(simplejson.dumps(
        {JSON_PAGE_EXPORT_NAME: JSON_PAGE_EXPORT_VERSION,
            'pages': [page.dump_json_data() for page in queryset]},
        indent=JSON_PAGE_EXPORT_INDENT, sort_keys=True))
    return response
export_pages_as_json.short_description = _("Export pages as JSON")

@transaction.commit_on_success
def import_pages_from_json(request,
        template_name='admin/pages/page/import_pages.html'):
    try:
        d = simplejson.load(request.FILES['json'])
    except KeyError:
        return redirect('admin:page-index')

    try:
        errors = validate_pages_json_data(d, get_language_from_request(request))
    except KeyError, e:
        errors = [_('JSON file is invalid: %s') % (e.args[0],)]

    pages_created = []
    if not errors:
        # pass one
        for p in d['pages']:
            pages_created.append(
                Page.objects.create_and_update_from_json_data(p, request.user))
        # pass two
        for p, results in zip(d['pages'], pages_created):
            page, created, messages = results
            rtcs = p['redirect_to_complete_slug']
            if rtcs:
                messages.extend(page.update_redirect_to_from_json(rtcs))

    return render_to_response(template_name, {
        'errors': errors,
        'pages_created': pages_created,
        'app_label': 'pages',
        'opts': Page._meta,
    }, RequestContext(request))

def validate_pages_json_data(d, preferred_lang):
    """
    Check if an import of d will succeed, and return errors.

    errors is a list of strings.  The import should proceed only if errors
    is empty.
    """
    errors = []

    seen_complete_slugs = dict(
        (lang[0], set()) for lang in settings.PAGE_LANGUAGES)

    valid_templates = set(t[0] for t in settings.get_page_templates())
    valid_templates.add(global_settings.PAGE_DEFAULT_TEMPLATE)

    if d[JSON_PAGE_EXPORT_NAME] != JSON_PAGE_EXPORT_VERSION:
        return [_('Unsupported file version: %s') % repr(
            d[JSON_PAGE_EXPORT_NAME])], []
    pages = d['pages']
    for p in pages:
        # use the complete slug as a way to identify pages in errors
        slug = p['complete_slug'].get(preferred_lang, None)
        seen_parent = False
        for lang, s in p['complete_slug'].items():
            if lang not in seen_complete_slugs:
                continue
            seen_complete_slugs[lang].add(s)

            if '/' not in s: # root level, no parent req'd
                seen_parent = True
            if not seen_parent:
                parent_slug, ignore = s.rsplit('/', 1)
                if parent_slug in seen_complete_slugs[lang]:
                    seen_parent = True
                elif Page.objects.from_path(parent_slug, lang,
                        exclude_drafts=False):
                    # parent not included, but exists on site
                    seen_parent = True
            if not slug:
                slug = s

        if not slug:
            errors.append(_("%s has no common language with this site")
                % (p['complete_slug'].values()[0],))
            continue

        if not seen_parent:
            errors.append(_("%s did not include its parent page and a matching"
                " one was not found on this site") % (slug,))

        if p['template'] not in valid_templates:
            errors.append(_("%s uses a template not found on this site: %s")
                % (slug, p['template']))
            continue

        if set(p.name for p in get_placeholders(p['template']) if
                p.name not in ('title', 'slug')) != set(p['content'].keys()):
            errors.append(_("%s template contents are different than our "
                "template: %s") % (slug, p['template']))
            assert 0, (set(p.name for p in get_placeholders(p['template'])),
                set(
                                p['content'].keys()))
            continue

    return errors





