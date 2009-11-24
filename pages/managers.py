# -*- coding: utf-8 -*-
"""Django page CMS ``managers``."""
import itertools, re
from datetime import datetime
from django.db import models, connection
from django.contrib.sites.managers import CurrentSiteManager
from django.contrib.sites.models import Site
from django.db.models import Q
from django.core.cache import cache

from pages import settings
from pages.utils import normalize_url, filter_link
from django.contrib.auth.models import User

class PageManager(models.Manager):
    """
    Page manager provide several filters to obtain pages :class:`QuerySet`
    that respect the page settings.
    """

    def populate_pages(self, parent=None, child=5, depth=5):
        """Create a population of pages for testing purpose."""
        from pages.models import Content
        author = User.objects.all()[0]
        if depth==0:
            return
        p = self.model(parent=parent, author=author,
            status=self.model.PUBLISHED)
        p.save()
        Content(body='page-'+str(p.id), type='title',
            language='en-us', page=p).save()
        Content(body='page-'+str(p.id), type='slug',
            language='en-us', page=p).save()
        for child in range(1, child):
            self.populate_pages(parent=p, child=child, depth=(depth-1))
    
    def on_site(self, site_id=None):
        """Return a :class:`QuerySet` of pages that are published on the site
        defined by the ``SITE_ID`` setting.

        :param site_id: specify the id of the site object to filter with.
        """
        if settings.PAGE_USE_SITE_ID:
            if not site_id:
                site_id = settings.SITE_ID
            return self.filter(sites=site_id)
        return self

    def root(self):
        """Return a :class:`QuerySet` of pages without parent."""
        return self.filter(parent__isnull=True)

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
            queryset = queryset.filter(sites=settings.SITE_ID)

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
        """Creates a :class:`QuerySet` of published filter."""
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
        from pages.models import Content, Page
        from pages.http import get_slug_and_relative_path
        slug, path, lang = get_slug_and_relative_path(complete_path, lang)
        page_ids = Content.objects.get_page_ids_by_slug(slug)
        pages_list = self.on_site().filter(id__in=page_ids)
        if exclude_drafts:
            pages_list = pages_list.exclude(status=Page.DRAFT)
        current_page = None
        if len(pages_list) == 1:
            return pages_list[0]
        # more than one page matching the slug, let's use the full url
        if len(pages_list) > 1:
            for page in pages_list:
                if page.get_url(lang) == complete_path:
                    return page
        return None

class ContentManager(models.Manager):
    """:class:`Content <pages.models.Content>` manager methods"""

    def sanitize(self, content):
        """Sanitize a string in order to avoid possible XSS using
        ``html5lib``."""
        import html5lib
        from html5lib import sanitizer
        p = html5lib.HTMLParser(tokenizer=sanitizer.HTMLSanitizer)
        # we need to remove <html><head/><body>...</body></html>
        return p.parse(content).toxml()[19:-14]

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

    def get_content(self, page, language, ctype, language_fallback=False):
        """Gets the latest :class:`Content <pages.models.Content>`
        for a particular page and language. Falls back to another
        language if wanted.

        :param page: the concerned page object.
        :param language: the wanted language.
        :param ctype: the content type.
        :param language_fallback: fallback to another language if ``True``.
        """
        PAGE_CONTENT_DICT_KEY = "page_content_dict_%s_%s"
        if not language:
            language = settings.PAGE_DEFAULT_LANGUAGE

        content_dict = cache.get(PAGE_CONTENT_DICT_KEY % (str(page.id), ctype))
        #content_dict = None

        if not content_dict:
            content_dict = {}
            for lang in settings.PAGE_LANGUAGES:
                try:
                    content = self.filter(
                        language=lang[0],
                        type=ctype,
                        page=page
                    ).latest()
                    content_dict[lang[0]] = content.body
                except self.model.DoesNotExist:
                    content_dict[lang[0]] = ''
            cache.set(PAGE_CONTENT_DICT_KEY % (page.id, ctype), content_dict)

        if language in content_dict and content_dict[language]:
            return filter_link(content_dict[language], page, language, ctype)

        if language_fallback:
            for lang in settings.PAGE_LANGUAGES:
                if lang[0] in content_dict and content_dict[lang[0]]:
                    return filter_link(content_dict[lang[0]], page, lang[0], ctype)
        return ''

    def get_content_slug_by_slug(self, slug):
        """Returns the latest :class:`Content <pages.models.Content>`
        slug object that match the given slug for the current site domain.

        :param slug: the wanted slug.
        """
        content = self.filter(type='slug', body=slug)
        if settings.PAGE_USE_SITE_ID:
            content = content.filter(page__sites__id=settings.SITE_ID)
        try:
           content = content.latest('creation_date')
        except self.model.DoesNotExist:
            return None
        else:
            return content

    def get_page_ids_by_slug(self, slug):
        """Return all page's id matching the given slug.

        :param slug: the wanted slug.
        """
        sql = '''SELECT pages_content.page_id,
            MAX(pages_content.creation_date)
            FROM pages_content WHERE (pages_content.type = %s
            AND pages_content.body =%s)
            GROUP BY pages_content.page_id'''
            
        cursor = connection.cursor()
        cursor.execute(sql, ('slug', slug, ))
        return [c[0] for c in cursor.fetchall()]

class PagePermissionManager(models.Manager):
    """Hierachic page permission manager."""

    def get_page_id_list(self, user):
        """Give a list of :class:`Page <pages.models.Page>` ids where the
        user has rights or the string
        "All" if the user has all rights.

        :param user: the interested user.
        """
        if user.is_superuser:
            return 'All'
        id_list = []
        for perm in self.filter(user=user):
            if perm.type == 0:
                return "All"
            if perm.page.id not in id_list:
                id_list.append(perm.page.id)
            if perm.type == 2:
                for page in perm.page.get_descendants():
                    if page.id not in id_list:
                        id_list.append(page.id)
        return id_list

class PageAliasManager(models.Manager):
    """:class:`PageAlias <pages.models.PageAlias>` manager."""
    
    def from_path(self, request, path, lang):
        """
        Resolve a request to an alias. returns a :class:`PageAlias <pages.models.PageAlias>`
        if the url matches no page at all. The aliasing system supports plain
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
