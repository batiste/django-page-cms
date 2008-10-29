from datetime import datetime

from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site

import mptt
from pages import settings
from pages.managers import PageManager, SitePageManager, ContentManager, PagePermissionManager

try:
    tagging = models.get_app('tagging')
    from tagging.fields import TagField
except ImproperlyConfigured:
    tagging = False

if not settings.PAGE_TAGGING:
    tagging = False

class Language(object):
    """
    A simple class to hold languages methods
    """
    def get_in_settings(cls, iso):
        for language in settings.PAGE_LANGUAGES:
            if language[0] == iso:
                return iso
        return None
    get_in_settings = classmethod(get_in_settings)
    
    def get_from_request(cls, request, current_page=None):
        """
        Return the most obvious language according the request
        """
        language = cls.get_in_settings(request.REQUEST.get('language', None))
        if language is None:
            language = getattr(request, 'LANGUAGE_CODE', None)
        if language is None:
            # in last resort, get the first language available in the page
            if current_page:
                languages = current_page.get_languages()
                if len(languages) > 0:
                    language = languages[0]
        if language is None:
            language = settings.PAGE_LANGUAGES[0]
        return language
    get_from_request = classmethod(get_from_request)


class Page(models.Model):
    """
    A simple hierarchical page model
    """
    # some class constants to refer to, e.g. Page.DRAFT
    DRAFT = 0
    PUBLISHED = 1
    STATUSES = (
        (DRAFT, _('Draft')),
        (PUBLISHED, _('Published')),
    )
    author = models.ForeignKey(User)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children')
    creation_date = models.DateTimeField(editable=False, default=datetime.now)
    publication_date = models.DateTimeField(editable=False, null=True)

    status = models.IntegerField(choices=STATUSES, default=DRAFT)
    template = models.CharField(max_length=100, null=True, blank=True)
    sites = models.ManyToManyField(Site, null=True, blank=True, default=[settings.SITE_ID], help_text=_('The site(s) the page is accessible at.'))

    # Managers
    objects = PageManager()
    on_site = SitePageManager('sites')

    if tagging:
        tags = TagField()

    class Meta:
        verbose_name = _('page')
        verbose_name_plural = _('pages')

    def save(self):
        if self.status == self.PUBLISHED and self.publication_date is None:
            self.publication_date = datetime.now()
        if not self.status:
            self.status = self.DRAFT
        super(Page, self).save()

    def get_admin_url(self):
        return '/admin/pages/page/%d/' % self.id

    def get_absolute_url(self):
        return reverse('pages-root') + self.get_url()

    def get_languages(self):
        """
        get the list of all existing languages for this page
        """
        contents = Content.objects.filter(page=self, type="title")
        languages = []
        for c in contents:
            if c.language not in languages:
                languages.append(c.language)
        return languages

    def get_url(self):
        """
        get the url of this page, adding parent's slug
        """
        url = "%s-%d/" % (self.slug(), self.id)
        an = self.get_ancestors()
        for p in an:
            url = p.slug() + '/' + url
        return url

    def slug(self, language=None, fallback=True):
        """
        get the slug of the page depending on the given language
        """
        if language is None:
            language = settings.PAGE_LANGUAGES[0][0]
        return Content.objects.get_content(self, language, 'slug',
                                           language_fallback=fallback)

    def get_template(self):
        """
        get the template of this page if defined or if closer parent if
        defined or DEFAULT_PAGE_TEMPLATE otherwise
        """
        if self.template:
            return self.template
        for p in self.get_ancestors(ascending=True):
            if p.template:
                return p.template
        return settings.DEFAULT_PAGE_TEMPLATE

    def traductions(self):
        langs = ""
        for lang in self.get_languages():
            langs += '%s, ' % lang
        return langs[0:-2]

    def has_page_permission(self, request):
        """
        Return true if the current user has permission on the page.
        Return the string 'All' if the user has all rights.
        """
        if not settings.PAGE_PERMISSION:
            return True
        else:
            permission = PagePermission.objects.get_page_id_list(request.user)
            if permission == "All":
                return True
            if page.id in permission:
                return True
            return False

    def __unicode__(self):
        return self.slug()
    
mptt.register(Page)

if settings.PAGE_PERMISSION:
    class PagePermission(models.Model):
        """
        Page permission object
        """
        TYPES = (
            (0, _('All')),
            (1, _('This page only')),
            (2, _('This page and all childrens')),
        )
        page = models.ForeignKey(Page, null=True, blank=True)
        user = models.ForeignKey(User)
        type = models.IntegerField(choices=TYPES, default=0)
        
        objects = PagePermissionManager()
        
        def __unicode__(self):
            return "%s :: %s" % (self.user, unicode(PagePermission.TYPES[self.type][1]))

class Content(models.Model):
    """A block of content, tied to a page, for a particular language"""
    language = models.CharField(max_length=3, blank=False)
    body = models.TextField()
    type = models.CharField(max_length=100, blank=False)
    page = models.ForeignKey(Page)

    creation_date = models.DateTimeField(editable=False, default=datetime.now)
    objects = ContentManager()

    def __unicode__(self):
        return "%s :: %s" % (self.page.slug(), self.body[0:15])

def has_page_add_permission(request, page=None):
    """
    Return true if the current user has permission to add a new page.
    """
    if not settings.PAGE_PERMISSION:
        return True
    else:
        permission = PagePermission.objects.get_page_id_list(request.user)
        if permission == "All":
            return True
    return False
