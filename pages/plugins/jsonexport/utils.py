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


def dump_json_data(page):
    """
    Return a python dict representation of this page for use as part of
    a JSON export.
    """
    def content_langs_ordered():
        """
        Return a list of languages ordered by the page content
        with the latest creation date in each.  This will be used
        to maintain the state of the language_up_to_date template
        tag when a page is restored or imported into another site.
        """
        params = {'page': page}
        if page.freeze_date:
            params['creation_date__lte'] = page.freeze_date
        cqs = Content.objects.filter(**params)
        cqs = cqs.values('language').annotate(latest=Max('creation_date'))
        return [c['language'] for c in cqs.order_by('latest')]
    languages = content_langs_ordered()

    def language_content(ctype):
        return dict(
            (lang, page.get_content(lang, ctype, language_fallback=False))
            for lang in languages)

    def placeholder_content():
        """Return content of each placeholder in each language."""
        out = {}
        for p in get_placeholders(page.get_template()):
            if p.ctype in ('title', 'slug'):
                continue  # these were already included
            out[p.name] = language_content(p.name)
        return out

    def isoformat(d):
        return None if d is None else d.strftime(ISODATE_FORMAT)

    def custom_email(user):
        """Allow a user's profile to return an email for the user."""
        return user.email

    tags = []
    if settings.PAGE_TAGGING:
        tags = [tag.name for tag in page.tags.all()]

    return {
        'complete_slug': dict(
            (lang, page.get_complete_slug(lang, hideroot=False))
            for lang in languages),
        'title': language_content('title'),
        'author_email': custom_email(page.author),
        'creation_date': isoformat(page.creation_date),
        'publication_date': isoformat(page.publication_date),
        'publication_end_date': isoformat(page.publication_end_date),
        'last_modification_date': isoformat(page.last_modification_date),
        'status': {
            Page.PUBLISHED: 'published',
            Page.HIDDEN: 'hidden',
            Page.DRAFT: 'draft'}[page.status],
        'template': page.template,
        'sites': (
            [site.domain for site in page.sites.all()]
            if settings.PAGE_USE_SITE_ID else []),
        'redirect_to_url': page.redirect_to_url,
        'redirect_to_complete_slug': dict(
            (lang, page.redirect_to.get_complete_slug(
                lang, hideroot=False))
            for lang in page.redirect_to.get_languages()
            ) if page.redirect_to is not None else None,
        'content': placeholder_content(),
        'content_language_updated_order': languages,
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
    """
    Create or update page based on python dict d loaded from JSON data.
    This applies all data except for redirect_to, which is done in a
    second pass after all pages have been imported,

    user is the User instance that will be used if the author can't
    be found in the DB.

    returns (page object, created, messages).

    created is True if this was a new page or False if an existing page
    was updated.

    messages is a list of strings warnings/messages about this import
    """
    page = None
    parent = None
    parent_required = True
    created = False
    messages = []

    page_languages = set(lang[0] for lang in settings.PAGE_LANGUAGES)

    for lang, s in list(d['complete_slug'].items()):
        if lang not in page_languages:
            messages.append(_("Language '%s' not imported") % (lang,))
            continue

        page = Page.objects.from_path(s, lang, exclude_drafts=False)
        if page and page.get_complete_slug(lang) == s:
            break
        if parent_required and parent is None:
            if '/' in s:
                parent = Page.objects.from_path(s.rsplit('/', 1)[0], lang,
                    exclude_drafts=False)
            else:
                parent_required = False
    else:
        # can't find an existing match, need to create a new Page
        page = Page(parent=parent)
        created = True

    user_model = get_user_model()

    def custom_get_user_by_email(email):
        """
        Simplified version
        """
        return user_model.objects.get(email=email)

    try:
        page.author = custom_get_user_by_email(d['author_email'])
    except (user_model.DoesNotExist, user_model.MultipleObjectsReturned):
        page.author = user
        messages.append(_("Original author '%s' not found")
            % (d['author_email'],))

    page.creation_date = datetime.strptime(d['creation_date'],
        ISODATE_FORMAT)
    page.publication_date = datetime.strptime(d['publication_date'],
        ISODATE_FORMAT) if d['publication_date'] else None
    page.publication_end_date = datetime.strptime(d['publication_end_date'],
        ISODATE_FORMAT) if d['publication_end_date'] else None
    page.last_modification_date = datetime.strptime(
        d['last_modification_date'], ISODATE_FORMAT)
    page.status = {
        'published': Page.PUBLISHED,
        'hidden': Page.HIDDEN,
        'draft': Page.DRAFT,
        }[d['status']]
    page.template = d['template']
    page.redirect_to_url = d['redirect_to_url']

    page.save()

    # Add tags
    if settings.PAGE_TAGGING:
        from taggit.models import Tag
        tags = d.get('tags', [])
        page.tags.clear()
        if tags:
            for tag in tags:
                Tag.objects.get_or_create(name=tag)
                page.tags.add(tag)
            page.save()

    if settings.PAGE_USE_SITE_ID:
        if d['sites']:
            for site in d['sites']:
                try:
                    page.sites.add(Site.objects.get(domain=site))
                except Site.DoesNotExist:
                    messages.append(_("Could not add site '%s' to page")
                        % (site,))
        if not settings.PAGE_HIDE_SITES and not page.sites.count():
            # need at least one site
            page.sites.add(Site.objects.get(pk=global_settings.SITE_ID))

    def create_content(lang, ctype, body):
        Content.objects.create_content_if_changed(page, lang, ctype, body)

    for lang in d['content_language_updated_order']:
        if lang not in page_languages:
            continue
        create_content(lang, 'slug',
            d['complete_slug'][lang].rsplit('/', 1)[-1])
        create_content(lang, 'title', d['title'][lang])
        for ctype, langs_bodies in list(d['content'].items()):
            create_content(lang, ctype, langs_bodies[lang])

    return page, created, messages


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
    """
    Check if an import of d will succeed, and return errors.

    errors is a list of strings.  The import should proceed only if errors
    is empty.
    """
    from pages.models import Page
    errors = []

    seen_complete_slugs = dict(
        (lang[0], set()) for lang in settings.PAGE_LANGUAGES)

    valid_templates = set(t[0] for t in settings.get_page_templates())
    valid_templates.add(settings.PAGE_DEFAULT_TEMPLATE)

    if d[JSON_PAGE_EXPORT_NAME] != JSON_PAGE_EXPORT_VERSION:
        return [_('Unsupported file version: %s') % repr(
            d[JSON_PAGE_EXPORT_NAME])], []
    pages = d['pages']
    for p in pages:
        # use the complete slug as a way to identify pages in errors
        slug = p['complete_slug'].get(preferred_lang, None)
        seen_parent = False
        for lang, s in list(p['complete_slug'].items()):
            if lang not in seen_complete_slugs:
                continue
            seen_complete_slugs[lang].add(s)

            if '/' not in s:  # root level, no parent req'd
                seen_parent = True
            if not seen_parent:
                parent_slug, ignore = s.rsplit('/', 1)
                if parent_slug in seen_complete_slugs[lang]:
                    seen_parent = True
                else:
                    parent = Page.objects.from_path(parent_slug, lang,
                        exclude_drafts=False)
                    if parent and parent.get_complete_slug(lang) == parent_slug:
                        # parent not included, but exists on site
                        seen_parent = True
            if not slug:
                slug = s

        if not slug:
            errors.append(_("%s has no common language with this site")
                % (list(p['complete_slug'].values())[0],))
            continue

        if not seen_parent:
            errors.append(_("%s did not include its parent page and a matching"
                " one was not found on this site") % (slug,))

        if p['template'] not in valid_templates:
            errors.append(_("%s uses a template not found on this site: %s")
                % (slug, p['template']))
            continue

        if set(p.ctype for p in get_placeholders(p['template']) if
                p.ctype not in ('title', 'slug')) != set(p['content'].keys()):
            errors.append(_("%s template contents are different than our "
                "template: %s") % (slug, p['template']))
            continue

    return errors
