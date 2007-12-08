from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _

class Language(models.Model):
    """A simple model to bescribe available languages for pages"""
    id = models.CharField(primary_key=True, max_length=8)
    name = models.CharField(maxlength=20)
    
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
    parent = models.ForeignKey('self', related_name="children", blank=True, null=True)
    creation_date = models.DateTimeField(editable=False, auto_now_add=True)
    publication_date = models.DateTimeField(editable=False, null=True)
    
    status = models.IntegerField(choices=STATUSES, radio_admin=True, default=0)
    template = models.CharField(maxlength=100, null=True, blank=True)
    order = models.IntegerField()

    # Managers
    objects = models.Manager()
    published = PagePublishedManager()
    drafts = PageDraftsManager()

    class Admin:
        pass
    
    class Meta:
        ordering = ['order']

    def save(self):
        self.slug = slugify(self.slug)
        if self.status == 1 and self.publication_date is None:
            from datetime import datetime
            self.publication_date = datetime.now()
        if not self.status:
            self.status = 0
        recalculate_order = False
        if not self.order:
            self.order=1
            recalculate_order = True
        super(Page, self).save()
        # not so proud of this code
        if recalculate_order:
            self.set_default_order()
            super(Page, self).save()
        
    def set_default_order(self):
        max = 0
        brothers = self.brothers()
        if brothers.count():
            for brother in brothers:
                if brother.order > max:
                    max = brother.order
        self.order = max + 1
    
    def brothers_and_me(self):
        if self.parent:
            return Page.objects.filter(parent=self.parent)
        else:
            return Page.objects.filter(parent__isnull=True)
        
    def brothers(self):
        return self.brothers_and_me().exclude(pk=self.id)
        
    def is_first(self):
        return self.brothers_and_me().order_by('order')[0:1][0] == self
    
    def is_last(self):
        return self.brothers_and_me().order_by('-order')[0:1][0] == self
        
    @classmethod
    def switch_page(cls, page1, page2):
        buffer =  page1.order
        page1.order = page2.order
        page2.order = buffer
        page1.save()
        page2.save()
        
    def up(self):
        brother = self.brothers().order_by('-order').filter(order__lt=self.order)[0:1]
        if not brother.count():
            return False
        Page.switch_page(self, brother[0])
        return True
        
    def down(self):
        brother = self.brothers().order_by('order').filter(order__gt=self.order)[0:1]
        if not brother.count():
            return False
        Page.switch_page(self, brother[0])
        return True

    def title(self, lang):
        c = Content.get_content(self, lang, 0, True)
        return c
    
    def body(self, lang):
        c = Content.get_content(self, lang, 1, True)
        return c
    
    def get_absolute_url(self):
        return '/pages/'+self.get_url()
    
    def get_languages(self):
        """get the list of all existing languages for this page"""
        contents = Content.objects.filter(page=self, type=1)
        languages = []
        for c in contents:
            languages.append(c.language.id)
        return languages
        
    def get_url(self):
        """get the url of this page, adding parent's slug"""
        url = self.slug + '/'
        p = self.parent
        while p:
            url = p.slug + '/' + url
            p = p.parent

        return url
        
    def get_template(self):
        """get the template of this page if defined 
        or if closer parent if defined or None otherwise"""
        p = self
        while p:
            if p.template:
                return p.template
            if p.parent:
                p = p.parent
            else:
                return None

    def __str__(self):
        if self.parent:
            return "%s :: %s :: %d" % (self.parent.slug, self.slug, self.order)
        else:
            return "%s :: %d" % (self.slug, self.order)
        
class Content(models.Model):
    """A block of content, tied to a page, for a particular language"""
    CONTENT_TYPE = ((0, 'title'),(1,'body'))
    language = models.ForeignKey(Language)
    body = models.TextField()
    type = models.IntegerField(choices=CONTENT_TYPE, radio_admin=True, default=0)
    page = models.ForeignKey(Page)
    
    class Admin:
        pass
    
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

