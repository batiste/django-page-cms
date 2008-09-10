from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
#from hierarchical.models import HierarchicalNode
import mptt
import settings

class Language(models.Model):
    """A simple model to bescribe available languages for pages"""
    id = models.CharField(primary_key=True, max_length=8)
    name = models.CharField(max_length=20)
    
    def __str__(self):
        return self.name
    
    @classmethod
    def get_from_request(cls, request, current_page=None):
        """Return the most obvious language according the request"""
        l = None
        if 'language' in request.GET:
            l = Language.objects.get(pk=request.GET['language'])
        elif 'language' in request.POST:
            l = Language.objects.get(pk=request.POST['language'])
        else:
            try:
                l = Language.objects.get(pk=request.LANGUAGE_CODE)
            except Language.DoesNotExist:
                # in last resort, get the first lanugage available in the page
                if current_page:
                    languages = current_page.get_languages()
                    if len(languages) > 0:
                        l = Language.objects.get(pk=languages[0])
        if l is None:
            l = Language.objects.latest('id')
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
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children')
    creation_date = models.DateTimeField(editable=False, auto_now_add=True)
    publication_date = models.DateTimeField(editable=False, null=True)
    
    status = models.IntegerField(choices=STATUSES, default=0)
    template = models.CharField(max_length=100, null=True, blank=True)

    # Managers
    objects = models.Manager()
    published = PagePublishedManager()
    drafts = PageDraftsManager()

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
        for p in self.get_ancestors():
            url = p.slug + '/' + url
        return url
        
    def get_template(self):
        """get the template of this page if defined 
        or if closer parent if defined or DEFAULT_PAGE_TEMPLATE otherwise"""
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

    def __str__(self):
        return "%s" % (self.slug)
    
mptt.register(Page, order_insertion_by=['slug'])

if settings.PAGE_PERMISSION:
    class PagePermission(models.Model):
        """Page permission object"""
        
        TYPES = (
            (0, _('All')),
            (1, _('This page only')),
            (2, _('This page and all childrens')),
        )
        
        page = models.ForeignKey(Page, null=True, blank=True)
        user = models.ForeignKey(User)
        type = models.IntegerField(choices=TYPES, default=0)
        
        @classmethod
        def get_page_id_list(cls, user):
            """Give a list of page where the user as rights or the string "All" if 
            the user has all rights."""
            if user.is_superuser:
                return 'All'
            id_list = []
            perms = PagePermission.objects.filter(user=user)
            for perm in perms:
                if perm.type == 0:
                    return "All"
                if perm.page.id not in id_list:
                    id_list.append(perm.page.id)
                if perm.type == 2:
                    for page in perm.page.get_descendants():
                        if page.id not in id_list:
                            id_list.append(page.id)
            return id_list

def get_page_valid_targets_queryset(request, page=None):
    """Give valid targets to move a page into the tree"""
    if not settings.PAGE_PERMISSION:
        perms = "All"
    else: 
        perms = PagePermission.get_page_id_list(request.user)
    exclude_list = []
    if page:
        exclude_list.append(page.id)
        for p in page.get_descendants():
            exclude_list.append(p.id)
    if perms != "All":
        return Page.objects.filter(id__in=perms).exclude(id__in=exclude_list)
    else:
        return Page.objects.exclude(id__in=exclude_list)

def has_page_permission(request, page):
    """
    Return true if the current user has permission on the page.
    Return the string 'All' if the user has all rights.
    """
    if not settings.PAGE_PERMISSION:
        return True
    else:
        permission = PagePermission.get_page_id_list(request.user)
        if permission == "All":
            return True
        if page.id in permission:
            return True
        return False
    
def has_page_add_permission(request, page=None):
    """
    Return true if the current user has permission to add a new page.
    """
    if not settings.PAGE_PERMISSION:
        return True
    else:
        permission = PagePermission.get_page_id_list(request.user)
        if permission == "All":
            return True
    return False

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

