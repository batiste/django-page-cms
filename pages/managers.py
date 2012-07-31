# -*- coding: utf-8 -*-
"""Django page CMS ``managers``."""
from pages import settings
from pages.utils import normalize_url, filter_link
from pages.http import get_slug

from django.db import models, connection
from django.db.models import Q
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User, SiteProfileNotAvailable
from django.db.models import Avg, Max, Min, Count
from django.contrib.sites.models import Site
from django.conf import settings as global_settings
from django.utils.translation import ugettext_lazy as _

from mptt.managers import TreeManager

from datetime import datetime

ISODATE_FORMAT = '%Y-%m-%dT%H:%M:%S.%f' # for parsing dates from JSON


class PageManager(TreeManager):
    """
    Page manager provide several filters to obtain pages :class:`QuerySet`
    that respect the page attributes and project settings.
    """

    if settings.PAGE_HIDE_SITES:
        def get_query_set(self):
            """Restrict operations to pages on the current site."""
            return super(PageManager, self).get_query_set().filter(
                sites=global_settings.SITE_ID)

    def populate_pages(self, parent=None, child=5, depth=5):
        """Create a population of :class:`Page <pages.models.Page>`
        for testing purpose."""
        from pages.models import Content
        author = User.objects.all()[0]
        if depth == 0:
            return
        p = self.model(parent=parent, author=author,
            status=self.model.PUBLISHED)
        p.save()
        p = self.get(id=p.id)
        Content(body='page-' + str(p.id), type='title',
            language=settings.PAGE_DEFAULT_LANGUAGE, page=p).save()
        Content(body='page-' + str(p.id), type='slug',
            language=settings.PAGE_DEFAULT_LANGUAGE, page=p).save()
        for child in range(1, child + 1):
            self.populate_pages(parent=p, child=child, depth=(depth - 1))

    def on_site(self, site_id=None):
        """Return a :class:`QuerySet` of pages that are published on the site
        defined by the ``SITE_ID`` setting.

        :param site_id: specify the id of the site object to filter with.
        """
        if settings.PAGE_USE_SITE_ID:
            if not site_id:
                site_id = global_settings.SITE_ID
            return self.filter(sites=site_id)
        return self.all()

    def root(self):
        """Return a :class:`QuerySet` of pages without parent."""
        return self.on_site().filter(parent__isnull=True)

    def navigation(self):
        """Creates a :class:`QuerySet` of the published root pages."""
        return self.on_site().filter(
                status=self.model.PUBLISHED).filter(parent__isnull=True)

    def hidden(self):
        """Creates a :class:`QuerySet` of the hidden pages."""
        return self.on_site().filter(status=self.model.HIDDEN)

    def filter_published(self, queryset):
        """Filter the given pages :class:`QuerySet` to obtain only published
        page."""
        if settings.PAGE_USE_SITE_ID:
            queryset = queryset.filter(sites=global_settings.SITE_ID)

        queryset = queryset.filter(status=self.model.PUBLISHED)

        if settings.PAGE_SHOW_START_DATE:
            queryset = queryset.filter(publication_date__lte=datetime.now())

        if settings.PAGE_SHOW_END_DATE:
            queryset = queryset.filter(
                Q(publication_end_date__gt=datetime.now()) |
                Q(publication_end_date__isnull=True)
            )

        return queryset

    def published(self):
        """Creates a :class:`QuerySet` of published
        :class:`Page <pages.models.Page>`."""
        return self.filter_published(self)

    def drafts(self):
        """Creates a :class:`QuerySet` of drafts using the page's
        :attr:`Page.publication_date`."""
        pub = self.on_site().filter(status=self.model.DRAFT)
        if settings.PAGE_SHOW_START_DATE:
            pub = pub.filter(publication_date__gte=datetime.now())
        return pub

    def expired(self):
        """Creates a :class:`QuerySet` of expired using the page's
        :attr:`Page.publication_end_date`."""
        return self.on_site().filter(
            publication_end_date__lte=datetime.now())

    def from_path(self, complete_path, lang, exclude_drafts=True):
        """Return a :class:`Page <pages.models.Page>` according to
        the page's path."""
        if complete_path.endswith("/"):
            complete_path = complete_path[:-1]
        # just return the root page
        if complete_path == '':
            root_pages = self.root()
            if root_pages:
                return root_pages[0]
            else:
                return None

        slug = get_slug(complete_path)
        from pages.models import Content
        page_ids = Content.objects.get_page_ids_by_slug(slug)
        pages_list = self.on_site().filter(id__in=page_ids)
        if exclude_drafts:
            pages_list = pages_list.exclude(status=self.model.DRAFT)
        if len(pages_list) == 1:
            if(settings.PAGE_USE_STRICT_URL and
                pages_list[0].get_complete_slug(lang) != complete_path):
                    return None
            return pages_list[0]
        # if more than one page is matching the slug,
        # we need to use the full URL
        if len(pages_list) > 1:
            for page in pages_list:
                if page.get_complete_slug(lang) == complete_path:
                    return page
        return None

    def create_and_update_from_json_data(self, d, user):
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

        for lang, s in d['complete_slug'].items():
            if lang not in page_languages:
                messages.append(_("Language '%s' not imported") % (lang,))
                continue

            page = self.from_path(s, lang, exclude_drafts=False)
            if page and page.get_complete_slug(lang) == s:
                break
            if parent_required and parent is None:
                if '/' in s:
                    parent = self.from_path(s.rsplit('/', 1)[0], lang,
                        exclude_drafts=False)
                else:
                    parent_required = False
        else:
            # can't find an existing match, need to create a new Page
            page = self.model(parent=parent)
            created = True

        def custom_get_user_by_email(email):
            """
            Allow the user profile class to look up a user by email
            address
            """
            # bit of an unpleasant hack that requres the logged-in
            # user has a profile, but I don't want to reproduce the
            # code in get_profile() here
            try:
                profile = user.get_profile()
            except (SiteProfileNotAvailable, ObjectDoesNotExist):
                return User.objects.get(email=email)
            get_user_by_email = getattr(profile, 'get_user_by_email', None)
            if get_user_by_email:
                return get_user_by_email(email)
            return User.objects.get(email=email)

        try:
            page.author = custom_get_user_by_email(d['author_email'])
        except (User.DoesNotExist, User.MultipleObjectsReturned):
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
            'published': self.model.PUBLISHED,
            'hidden': self.model.HIDDEN,
            'draft': self.model.DRAFT,
            }[d['status']]
        page.template = d['template']
        page.redirect_to_url = d['redirect_to_url']

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

        from pages.models import Content
        def create_content(lang, ctype, body):
            Content.objects.create_content_if_changed(page, lang, ctype, body)

        for lang in d['content_language_updated_order']:
            if lang not in page_languages:
                continue
            create_content(lang, 'slug',
                d['complete_slug'][lang].rsplit('/', 1)[-1])
            create_content(lang, 'title', d['title'][lang])
            for ctype, langs_bodies in d['content'].items():
                create_content(lang, ctype, langs_bodies[lang])

        return page, created, messages



class ContentManager(models.Manager):
    """:class:`Content <pages.models.Content>` manager methods"""

    PAGE_CONTENT_DICT_KEY = "page_content_dict_%d_%s_%d"

    def sanitize(self, content):
        """Sanitize a string in order to avoid possible XSS using
        ``html5lib``."""
        import html5lib
        from html5lib import sanitizer
        p = html5lib.HTMLParser(tokenizer=sanitizer.HTMLSanitizer)
        dom_tree = p.parseFragment(content)
        return dom_tree.toxml()

    def set_or_create_content(self, page, language, ctype, body):
        """Set or create a :class:`Content <pages.models.Content>` for a
        particular page and language.

        :param page: the concerned page object.
        :param language: the wanted language.
        :param ctype: the content type.
        :param body: the content of the Content object.
        """
        if settings.PAGE_SANITIZE_USER_INPUT:
            body = self.sanitize(body)
        try:
            content = self.filter(page=page, language=language,
                                  type=ctype).latest('creation_date')
            content.body = body
        except self.model.DoesNotExist:
            content = self.model(page=page, language=language, body=body,
                                 type=ctype)
        content.save()
        return content

    def create_content_if_changed(self, page, language, ctype, body):
        """Create a :class:`Content <pages.models.Content>` for a particular
        page and language only if the content has changed from the last
        time.

        :param page: the concerned page object.
        :param language: the wanted language.
        :param ctype: the content type.
        :param body: the content of the Content object.
        """
        if settings.PAGE_SANITIZE_USER_INPUT:
            body = self.sanitize(body)
        try:
            content = self.filter(page=page, language=language,
                                  type=ctype).latest('creation_date')
            if content.body == body:
                return content
        except self.model.DoesNotExist:
            pass
        content = self.create(page=page, language=language, body=body,
                type=ctype)

        # Delete old revisions
        if settings.PAGE_CONTENT_REVISION_DEPTH:
            oldest_content = self.filter(page=page, language=language,
                type=ctype).order_by('-creation_date'
                )[settings.PAGE_CONTENT_REVISION_DEPTH:]
            for c in oldest_content:
                c.delete()

        return content

    def get_content_object(self, page, language, ctype):
        """Gets the latest published :class:`Content <pages.models.Content>`
        for a particular page, language and placeholder type."""
        params = {
            'language': language,
            'type': ctype,
            'page': page
        }
        if page.freeze_date:
            params['creation_date__lte'] = page.freeze_date
        return  self.filter(**params).latest()

    def get_content(self, page, language, ctype, language_fallback=False):
        """Gets the latest content string for a particular page, language and
        placeholder.

        :param page: the concerned page object.
        :param language: the wanted language.
        :param ctype: the content type.
        :param language_fallback: fallback to another language if ``True``.
        """
        if not language:
            language = settings.PAGE_DEFAULT_LANGUAGE

        frozen = int(bool(page.freeze_date))
        key = self.PAGE_CONTENT_DICT_KEY % (page.id, ctype, frozen)

        if page._content_dict is None:
            page._content_dict = dict()
        if page._content_dict.get(key, None):
            content_dict = page._content_dict.get(key)
        else:
            content_dict = cache.get(key)

        # fill a dict object for each language, that will create
        # P * L queries.
        # L == number of language, P == number of placeholder in the page.
        # Once generated the result is cached.
        if not content_dict:
            content_dict = {}
            for lang in settings.PAGE_LANGUAGES:
                try:
                    content = self.get_content_object(page, lang[0], ctype)
                    content_dict[lang[0]] = content.body
                except self.model.DoesNotExist:
                    content_dict[lang[0]] = ''
            page._content_dict[key] = content_dict
            cache.set(key, content_dict)

        if language in content_dict and content_dict[language]:
            return filter_link(content_dict[language], page, language, ctype)

        if language_fallback:
            for lang in settings.PAGE_LANGUAGES:
                if lang[0] in content_dict and content_dict[lang[0]]:
                    return filter_link(content_dict[lang[0]], page, lang[0],
                        ctype)
        return ''

    def get_content_slug_by_slug(self, slug):
        """Returns the latest :class:`Content <pages.models.Content>`
        slug object that match the given slug for the current site domain.

        :param slug: the wanted slug.
        """
        content = self.filter(type='slug', body=slug)
        if settings.PAGE_USE_SITE_ID:
            content = content.filter(page__sites__id=global_settings.SITE_ID)
        try:
            content = content.latest('creation_date')
        except self.model.DoesNotExist:
            return None
        else:
            return content

    def get_page_ids_by_slug(self, slug):
        """Return all page's id matching the given slug.
        This function also returns pages that have an old slug
        that match.

        :param slug: the wanted slug.
        """
        ids = self.filter(type='slug', body=slug).values('page_id').annotate(
            max_creation_date=Max('creation_date')
        )
        return [content['page_id'] for content in ids]


class PageAliasManager(models.Manager):
    """:class:`PageAlias <pages.models.PageAlias>` manager."""

    def from_path(self, request, path, lang):
        """
        Resolve a request to an alias. returns a
        :class:`PageAlias <pages.models.PageAlias>` if the url matches
        no page at all. The aliasing system supports plain
        aliases (``/foo/bar``) as well as aliases containing GET parameters
        (like ``index.php?page=foo``).

        :param request: the request object
        :param path: the complete path to the page
        :param lang: not used
        """
        from pages.models import PageAlias

        url = normalize_url(path)
        # §1: try with complete query string
        query = request.META.get('QUERY_STRING')
        if query:
            url = url + '?' + query
        try:
            alias = PageAlias.objects.get(url=url)
            return alias
        except PageAlias.DoesNotExist:
            pass
        # §2: try with path only
        url = normalize_url(path)
        try:
            alias = PageAlias.objects.get(url=url)
            return alias
        except PageAlias.DoesNotExist:
            pass
        # §3: not alias found, we give up
        return None
