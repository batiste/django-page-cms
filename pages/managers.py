# -*- coding: utf-8 -*-
import itertools
from datetime import datetime
from django.db import models, connection
from django.contrib.sites.managers import CurrentSiteManager
from django.contrib.sites.models import Site
from django.db.models import Q
from django.core.cache import cache
from pages import settings

class PageManager(models.Manager):
    
    def on_site(self, site_id=None):
        if settings.PAGE_USE_SITE_ID:
            if not site_id:
                site_id = settings.SITE_ID
            return self.filter(sites=site_id)
        return self

    def root(self):
        """
        Return a queryset with pages that don't have parents, a.k.a. root.
        """
        return self.filter(parent__isnull=True)

    def valid_targets(self, page_id, request, perms, page=None):
        """
        Give valid targets to move a page into the tree
        """
        if page is None:
            page = self.get(pk=page_id)
        exclude_list = []
        if page:
            exclude_list.append(page.id)
            for p in page.get_descendants():
                exclude_list.append(p.id)
        if perms != "All":
            return self.filter(id__in=perms).exclude(id__in=exclude_list)
        else:
            return self.exclude(id__in=exclude_list)

    def navigation(self):
        return self.on_site().filter(status=self.model.PUBLISHED).filter(parent__isnull=True)

    def hidden(self):
        return self.on_site().filter(status=self.model.HIDDEN)

    def filter_published(self, queryset):
        """Resuable filter for published page"""
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
        return self.filter_published(self)

    def drafts(self):
        pub = self.on_site().filter(status=self.model.DRAFT)
        if settings.PAGE_SHOW_START_DATE:
            pub = pub.filter(publication_date__gte=datetime.now())
        return pub

    def expired(self):
        return self.on_site().filter(
            publication_end_date__lte=datetime.now())

class ContentManager(models.Manager):

    def sanitize(self, content):
        """
        Sanitize the content to avoid XSS and so
        """
        import html5lib
        from html5lib import sanitizer
        p = html5lib.HTMLParser(tokenizer=sanitizer.HTMLSanitizer)
        # we need to remove <html><head/><body>...</body></html>
        return p.parse(content).toxml()[19:-14]

    def set_or_create_content(self, page, language, cnttype, body):
        """
        set or create a content for a particular page and language
        """
        if settings.PAGE_SANITIZE_USER_INPUT:
            body = self.sanitize(body)
        try:
            content = self.filter(page=page, language=language,
                                  type=cnttype).latest('creation_date')
            content.body = body
        except self.model.DoesNotExist:
            content = self.model(page=page, language=language, body=body,
                                 type=cnttype)
        content.save()
        return content

    def create_content_if_changed(self, page, language, cnttype, body):
        """
        set or create a content for a particular page and language
        """
        if settings.PAGE_SANITIZE_USER_INPUT:
            body = self.sanitize(body)
        try:
            content = self.filter(page=page, language=language,
                                  type=cnttype).latest('creation_date')
            if content.body == body:
                return content
        except self.model.DoesNotExist:
            pass
        content = self.create(page=page, language=language, body=body, type=cnttype)

    def get_content(self, page, language, ctype, language_fallback=False):
        """
        Gets the latest content for a particular page and language. Falls back
        to another language if wanted.
        """
        PAGE_CONTENT_DICT_KEY = "page_content_dict_%d_%s"
        if not language:
            language = settings.PAGE_DEFAULT_LANGUAGE

        content_dict = cache.get(PAGE_CONTENT_DICT_KEY % (page.id, ctype))
        #content_dict = None

        if not content_dict:
            content_dict = {}
            for lang in settings.PAGE_LANGUAGES:
                try:
                    content = self.filter(language=lang[0], type=ctype, page=page).latest()
                    content_dict[lang[0]] = content.body
                except self.model.DoesNotExist:
                    content_dict[lang[0]] = ''
            cache.set(PAGE_CONTENT_DICT_KEY % (page.id, ctype), content_dict)
        
        if content_dict[language]:
            return content_dict[language]

        if language_fallback:
            for lang in settings.PAGE_LANGUAGES:
                if content_dict[lang[0]]:
                    return content_dict[lang[0]]
        return ''

    def get_content_slug_by_slug(self, slug):
        """
        Returns the latest Content slug object that match the given slug for
        the current site domain.
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
        """
        Return all the page id according to a slug
        """
        sql = '''SELECT pages_content.page_id, MAX(pages_content.creation_date)
            FROM pages_content WHERE (pages_content.type = %s AND pages_content.body =%s)
            GROUP BY pages_content.page_id'''
            
        cursor = connection.cursor()
        cursor.execute(sql, ('slug', slug, ))
        return [c[0] for c in cursor.fetchall()]

class PagePermissionManager(models.Manager):
    
    def get_page_id_list(self, user):
        """
        Give a list of page where the user has rights or the string "All" if
        the user has all rights.
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
