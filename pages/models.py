from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from hierarchical.models import HierarchicalNode
import settings

class Language(models.Model):
    """A simple model to bescribe available languages for pages"""
    id = models.CharField(primary_key=True, max_length=8)
    name = models.CharField(max_length=20)
    
    def __str__(self):
        return self.name.capitalize()
    
    @classmethod
    def get_from_request(cls, request, current_page=None):
        """Return the most obvious language according the request"""
        if 'language' in request.GET:
            l=Language.objects.get(pk=request.GET['language'])
        elif 'language' in request.POST:
            l=Language.objects.get(pk=request.POST['language'])
        else:
            try:
                l=Language.objects.get(pk=request.LANGUAGE_CODE)
            except Language.DoesNotExist:
                # in last resort, get the first lanugage available in the page
                if current_page:
                    languages = current_page.get_languages()
                    if len(languages) > 0:
                        l=languages[0]
        if not l:
            l=Language.objects.latest('id')
        return l

class PagePublishedManager(models.Manager):
    def get_query_set(self):
        return super(PagePublishedManager, self).get_query_set().filter(status=1)
    
class PageDraftsManager(models.Manager):
    def get_query_set(self):
        return super(PageDraftsManager, self).get_query_set().filter(status=0)

class Page(models.Model):
    """A simple hierarchical page model"""

    STATUSES = (
        (0, _('Draft')),
        (1, _('Published'))
    )
    
    # slugs are the same for each language
    slug = models.SlugField(unique=True)
    author = models.ForeignKey(User)
    #parent = models.ForeignKey('self', related_name="children", blank=True, null=True)
    creation_date = models.DateTimeField(editable=False, auto_now_add=True)
    publication_date = models.DateTimeField(editable=False, null=True)
    
    status = models.IntegerField(choices=STATUSES, default=0)
    template = models.CharField(max_length=100, null=True, blank=True)

    # Managers
    objects = models.Manager()
    published = PagePublishedManager()
    drafts = PageDraftsManager()

    #class Admin:
    #    list_display = ('slug', 'traductions', 'nodes')
    
    #class Meta:
    #    ordering = ['order']

    def save(self):
        self.slug = slugify(self.slug)
        if self.status == 1 and self.publication_date is None:
            from datetime import datetime
            self.publication_date = datetime.now()
        if not self.status:
            self.status = 0
        super(Page, self).save()
    
    def title(self, lang):
        c = Content.get_content(self, lang, 0, True)
        return c
    
    def body(self, lang):
        c = Content.get_content(self, lang, 1, True)
        return c
    
    def get_admin_url(self):
        return '/admin/pages/page/%d/' % self.id
        
    def get_absolute_url(self):
        return '/pages/'+self.get_url()
    
    def get_languages(self):
        """get the list of all existing languages for this page"""
        contents = Content.objects.filter(page=self, type="title")
        languages = []
        for c in contents:
            languages.append(c.language.id)
        return languages
        
    def get_url(self):
        """get the url of this page, adding parent's slug"""
        url = "%s-%d/" % (self.slug, self.id)
        p = HierarchicalNode.get_parent_object(self)
        while p:
            url = p.slug + '/' + url
            p = HierarchicalNode.get_parent_object(p)
        return url
        
    def get_template(self):
        """get the template of this page if defined 
        or if closer parent if defined or DEFAULT_PAGE_TEMPLATE otherwise"""
        p = self
        while p:
            if not p:
                return settings.DEFAULT_PAGE_TEMPLATE
            if p.template:
                return p.template
            try:
                p = HierarchicalNode.get_parent_object(p)
            except HierarchicalNode.DoesNotExist:
                return settings.DEFAULT_PAGE_TEMPLATE
        return settings.DEFAULT_PAGE_TEMPLATE
        
    def traductions(self):
        langs = ""
        for lang in self.get_languages():
            langs += '%s, ' % lang
        return langs[0:-2]
        
    def nodes(self):
        nodes = ""
        for node in HierarchicalNode.get_nodes_by_object(self):
            nodes += '%s, ' % node.name
        return nodes[0:-2]

    def __str__(self):
        return "%s" % (self.slug)

class Content(models.Model):
    """A block of content, tied to a page, for a particular language"""
    language = models.ForeignKey(Language)
    body = models.TextField()
    type = models.CharField(max_length=100, blank=False)
    page = models.ForeignKey(Page)
    
    def __str__(self):
        return "%s :: %s" % (self.page.slug, self.body[0:15])
    
    @classmethod
    def set_or_create_content(cls, page, language, type, body):
        """set or create a content for a particular page and language"""
        try:
            c = Content.objects.get(page=page, language=language, type=type)
            c.body = body
        except Content.DoesNotExist:
            c = Content(page=page, language=language, body=body, type=type)
        c.save()
        return c
        
    @classmethod
    def get_content(cls, page, language, type, language_fallback=False):
        """get a content for a particular page and language. Fallback in another language if wanted"""
        try:
            c = Content.objects.get(language=language, page=page, type=type)
            return c.body
        except Content.DoesNotExist:
            if language_fallback:
                try:
                    c = Content.objects.filter(page=page, type=type)
                    if len(c):
                        return c[0].body
                except Content.DoesNotExist:
                    pass
        return None

