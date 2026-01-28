from django.db.models import Max
from django.utils.translation import ugettext_lazy as _
from django.contrib.sites.models import Site
from django.conf import settings as global_settings
from django.contrib.auth import get_user_model

from pages.models import Page, Content
from pages.managers import PageManager
from pages.utils import get_placeholders
from pages import settings

from datetime import datetime
import json as _json

ISODATE_FORMAT = '%Y-%m-%dT%H:%M:%S.%f'  # for parsing dates from JSON
JSON_PAGE_EXPORT_NAME = 'gerbi_cms_page_export_version'
JSON_PAGE_EXPORT_VERSION = 4
# make it readable -- there are better ways to save space
JSON_PAGE_EXPORT_INDENT = 2


def monkeypatch_remove_pages_site_restrictions():
    """
    monkeypatch PageManager to expose pages for all sites by
    removing customized get_query_set. Only actually matters
    if PAGE_HIDE_SITES is set
    """
    try:
        del PageManager.get_query_set
    except AttributeError:
        pass


# Helper for fetching content maps from a page
def get_lang_map(ctype, p_obj, languages, fallback=False):
    return {
        lang: p_obj.get_content(lang, ctype, language_fallback=fallback)
        for lang in languages
    }

def dump_json_data(page):
    """Return a dictionary representation of the page for JSON export."""
    
    # 1. Determine Language Order
    params = {'page': page}
    if page.freeze_date:
        params['creation_date__lte'] = page.freeze_date
    
    languages = (
        Content.objects.filter(**params)
        .values('language')
        .annotate(latest=Max('creation_date'))
        .order_by('latest')
        .values_list('language', flat=True)
    )

    # 2. Process Placeholders
    placeholders = get_placeholders(page.get_template())
    content_data = {
        p.name: get_lang_map(p.name, page, languages)
        for p in placeholders 
        if p.ctype not in ('title', 'slug')
    }

    # 3. Format Dates & Tags
    iso = lambda d: d.strftime(ISODATE_FORMAT) if d else None
    tags = [t.name for t in page.tags.all()] if settings.PAGE_TAGGING else []

    # 4. Build Final Dict
    return {
        'title': get_lang_map('title', page, languages),
        'complete_slug': {
            lang: page.get_complete_slug(lang, hideroot=False) 
            for lang in languages
        },
        'author_email': page.author.email,
        'creation_date': iso(page.creation_date),
        'publication_date': iso(page.publication_date),
        'publication_end_date': iso(page.publication_end_date),
        'last_modification_date': iso(page.last_modification_date),
        'status': page.get_status_display().lower(), # Assumes Django-style choices
        'template': page.template,
        'sites': [s.domain for s in page.sites.all()] if settings.PAGE_USE_SITE_ID else [],
        'redirect_to_url': page.redirect_to_url,
        'redirect_to_complete_slug': {
            lang: page.redirect_to.get_complete_slug(lang, hideroot=False)
            for lang in page.redirect_to.get_languages()
        } if page.redirect_to else None,
        'content': content_data,
        'content_language_updated_order': list(languages),
        'tags': tags,
    }


def update_redirect_to_from_json(page, redirect_to_complete_slugs):
    """
    The second pass of create_and_update_from_json_data
    used to update the redirect_to field.

    Returns a messages list to be appended to the messages from the
    first pass.
    """
    messages = []
    s = ''
    for lang, s in list(redirect_to_complete_slugs.items()):
        r = Page.objects.from_path(s, lang, exclude_drafts=False)
        if r:
            page.redirect_to = r
            page.save()
            break
    else:
        messages.append(_("Could not find page for redirect-to field"
            " '%s'") % (s,))
    return messages


def create_and_update_from_json_data(d, user):
    """Entry point: Orchestrates the creation/update of a Page."""
    messages = []
    page_languages = set(lang[0] for lang in settings.PAGE_LANGUAGES)

    # 1. Resolve Identity
    page, parent, created = _find_page_match(d, page_languages, messages)
    if not page:
        page = Page(parent=parent)
        created = True

    # 2. Update Basic Metadata
    _update_metadata(page, d, user, messages)
    page.save()

    # 3. Update Relationships (Tags & Sites)
    _update_relationships(page, d, messages)

    # 4. Sync Content
    _sync_content(page, d, page_languages)

    return page, created, messages

def _find_page_match(d, allowed_langs, messages):
    """Heuristic to find an existing page or its parent."""
    parent = None
    parent_required = True
    
    for lang, slug in d['complete_slug'].items():
        if lang not in allowed_langs:
            messages.append(_("Language '%s' not imported") % lang)
            continue

        page = Page.objects.from_path(slug, lang, exclude_drafts=False)
        if page and page.get_complete_slug(lang) == slug:
            return page, None, False
        
        if parent_required and not parent:
            if '/' in slug:
                parent = Page.objects.from_path(slug.rsplit('/', 1)[0], lang, exclude_drafts=False)
            else:
                parent_required = False
    return None, parent, True

def _update_metadata(page, d, default_user, messages):
    """Parses dates, author, and status."""
    user_model = get_user_model()
    try:
        page.author = user_model.objects.get(email=d['author_email'])
    except (user_model.DoesNotExist, user_model.MultipleObjectsReturned):
        page.author = default_user
        messages.append(_("Original author '%s' not found") % d['author_email'])

    # Date parsing
    to_date = lambda key: datetime.strptime(d[key], ISODATE_FORMAT) if d.get(key) else None
    page.creation_date = sobriety_check = to_date('creation_date')
    page.publication_date = to_date('publication_date')
    page.publication_end_date = to_date('publication_end_date')
    page.last_modification_date = to_date('last_modification_date')

    status_map = {'published': Page.PUBLISHED, 'hidden': Page.HIDDEN, 'draft': Page.DRAFT}
    page.status = status_map.get(d['status'], Page.DRAFT)
    page.template = d['template']
    page.redirect_to_url = d['redirect_to_url']

def _update_relationships(page, d, messages):
    """Handles Tags and Sites."""
    if settings.PAGE_TAGGING:
        page.tags.set(d.get('tags', [])) # Django-taggit supports .set()

    if settings.PAGE_USE_SITE_ID:
        for domain in d.get('sites', []):
            try:
                page.sites.add(Site.objects.get(domain=domain))
            except Site.DoesNotExist:
                messages.append(_("Could not add site '%s'") % domain)
        
        if not settings.PAGE_HIDE_SITES and not page.sites.exists():
            page.sites.add(Site.objects.get(pk=global_settings.SITE_ID))

def _sync_content(page, d, allowed_langs):
    """Iterates through content order and updates bodies."""
    for lang in d['content_language_updated_order']:
        if lang not in allowed_langs:
            continue
        
        # Sync Slug & Title
        short_slug = d['complete_slug'][lang].rsplit('/', 1)[-1]
        Content.objects.create_content_if_changed(page, lang, 'slug', short_slug)
        Content.objects.create_content_if_changed(page, lang, 'title', d['title'][lang])

        # Sync Placeholders
        for ctype, bodies in d['content'].items():
            if lang in bodies:
                Content.objects.create_content_if_changed(page, lang, ctype, bodies[lang])


def pages_to_json(queryset):
    """
    Return a JSON string export of the pages in queryset.
    """
    # selection may be in the wrong order, and order matters
    queryset = queryset.order_by('tree_id', 'lft')
    return _json.dumps(
        {JSON_PAGE_EXPORT_NAME: JSON_PAGE_EXPORT_VERSION,
            'pages': [dump_json_data(page) for page in queryset]},
        indent=JSON_PAGE_EXPORT_INDENT, sort_keys=True)


def json_to_pages(json, user, preferred_lang=None):
    """
    Attept to create/update pages from JSON string json.  user is the
    user that will be used when creating a page if a page's original
    author can't be found.  preferred_lang is the language code of the
    slugs to include in error messages (defaults to
    settings.PAGE_DEFAULT_LANGUAGE).

    Returns (errors, pages_created) where errors is a list of strings
    and pages_created is a list of: (page object, created bool,
    messages list of strings) tuples.

    If any errors are detected there the error list will contain
    information for the user and no pages will be created/updated.
    """
    from pages.models import Page
    if not preferred_lang:
        preferred_lang = settings.PAGE_DEFAULT_LANGUAGE

    d = _json.loads(json)
    try:
        errors = validate_pages_json_data(d, preferred_lang)
    except KeyError as e:
        errors = [_('JSON file is invalid: %s') % (e.args[0],)]

    pages_created = []
    if not errors:
        # pass one
        for p in d['pages']:
            pages_created.append(
                create_and_update_from_json_data(p, user))
        # pass two
        for p, results in zip(d['pages'], pages_created):
            page, created, messages = results
            rtcs = p['redirect_to_complete_slug']
            if rtcs:
                messages.extend(update_redirect_to_from_json(page, rtcs))
        # clean up MPTT links
        Page.objects.rebuild()

    return errors, pages_created


def validate_pages_json_data(d, preferred_lang):
    """Entry point: Validates the entire export dictionary."""
    if d.get(JSON_PAGE_EXPORT_NAME) != JSON_PAGE_EXPORT_VERSION:
        return [_('Unsupported file version: %s') % repr(d.get(JSON_PAGE_EXPORT_NAME))]

    errors = []
    # State tracker for slugs within this import batch
    seen_slugs_by_lang = {lang[0]: set() for lang in settings.PAGE_LANGUAGES}
    valid_templates = set(t[0] for t in settings.get_page_templates())
    valid_templates.add(settings.PAGE_DEFAULT_TEMPLATE)

    for page_data in d.get('pages', []):
        page_errors = _validate_page_integrity(
            page_data, 
            preferred_lang, 
            seen_slugs_by_lang, 
            valid_templates
        )
        errors.extend(page_errors)

    return errors

def _validate_page_integrity(p, preferred_lang, seen_slugs, valid_templates):
    """Validates an individual page entry against the site and the import batch."""
    errors = []
    slug_map = p.get('complete_slug', {})
    
    # 1. Determine an identifier for error messages
    display_slug = slug_map.get(preferred_lang) or next(iter(slug_map.values()), "Unknown Page")
    
    # 2. Language & Parent Validation
    has_valid_parent = False
    has_shared_language = False

    for lang, full_slug in slug_map.items():
        if lang not in seen_slugs:
            continue
        
        has_shared_language = True
        seen_slugs[lang].add(full_slug)

        if _has_accessible_parent(full_slug, lang, seen_slugs[lang]):
            has_valid_parent = True

    # 3. Collect Errors
    if not has_shared_language:
        errors.append(_("%s has no common language with this site") % display_slug)
        return errors # Break early if no language match

    if not has_valid_parent:
        errors.append(_("%s: Parent page not found in import or on site") % display_slug)

    if p['template'] not in valid_templates:
        errors.append(_("%(page)s uses invalid template: %(template)s") 
                      % {"page": display_slug, "template": p['template']})
    else:
        # Template Content Schema Check
        if not _check_placeholder_schema(p):
            errors.append(_("%(page)s content keys do not match template %(template)s") 
                          % {"page": display_slug, "template": p['template']})

    return errors

def _has_accessible_parent(slug, lang, seen_in_batch):
    """Returns True if the page is root or its parent exists locally or in the current batch."""
    if '/' not in slug:
        return True
    
    parent_path = slug.rsplit('/', 1)[0]
    if parent_path in seen_in_batch:
        return True
    
    # Check database
    from pages.models import Page
    parent = Page.objects.from_path(parent_path, lang, exclude_drafts=False)
    return parent and parent.get_complete_slug(lang) == parent_path

def _check_placeholder_schema(p):
    """Compares the JSON content keys against the actual template placeholders."""
    template_placeholders = set(
        ph.ctype for ph in get_placeholders(p['template']) 
        if ph.ctype not in ('title', 'slug')
    )
    import_placeholders = set(p['content'].keys())
    return template_placeholders == import_placeholders
