from django.db import models
from django.contrib.sites.managers import CurrentSiteManager

class PageManager(models.Manager):
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
    
    def published(self):
        return self.filter(status=self.model.PUBLISHED)

    def drafts(self):
        return self.filter(status=self.model.DRAFT)

class SitePageManager(PageManager, CurrentSiteManager):
    pass

class ContentManager(models.Manager):

    def set_or_create_content(self, page, language, type, body):
        """
        set or create a content for a particular page and language
        """
        try:
            content = self.filter(page=page, language=language,
                                  type=type).latest('creation_date')
            content.body = body
        except self.model.DoesNotExist:
            content = self.model(page=page, language=language, body=body,
                                 type=type)
        content.save()
        return content

    def create_content_if_changed(self, page, language, type, body):
        """
        set or create a content for a particular page and language
        """
        try:
            content = self.filter(page=page, language=language,
                                  type=type).latest('creation_date')
            if content.body == body:
                return content
        except self.model.DoesNotExist:
            pass
        content = self.create(page=page, language=language,
                                    body=body, type=type)

    def get_content(self, page, language, cnttype, language_fallback=False):
        """
        Gets the latest content for a particular page and language. Falls back
        to another language if wanted.
        """
        try:
            content = self.filter(language=language, page=page,
                                  type=cnttype).latest('creation_date')
            return content.body
        except self.model.DoesNotExist:
            pass
        if language_fallback:
            try:
                content = self.filter(page=page,
                                      type=cnttype).latest('creation_date')
                return content.body
            except self.model.DoesNotExist:
                pass
        return None

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
