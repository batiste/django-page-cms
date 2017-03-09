"""Django page CMS ``models``."""

from pages.cache import cache
from pages.utils import get_placeholders, normalize_url, get_now
from pages.managers import PageManager, ContentManager
from pages.managers import PageAliasManager
from pages import settings
from pages.utils import slugify
# checks
from pages import checks

from django.db import models
from django.conf import settings as django_settings
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse
from django.conf import settings as global_settings
from django.utils.encoding import python_2_unicode_compatible


from mptt.models import MPTTModel
import uuid
import os

PAGE_CONTENT_DICT_KEY = ContentManager.PAGE_CONTENT_DICT_KEY

if settings.PAGE_USE_SITE_ID:
    from django.contrib.sites.models import Site


@python_2_unicode_compatible
class Page(MPTTModel):
    """
    This model contain the status, dates, author, template.
    The real content of the page can be found in the
    :class:`Content <pages.models.Content>` model.

    .. attribute:: creation_date
       When the page has been created.

    .. attribute:: publication_date
       When the page should be visible.

    .. attribute:: publication_end_date
       When the publication of this page end.

    .. attribute:: last_modification_date
       Last time this page has been modified.

    .. attribute:: status
       The current status of the page. Could be DRAFT, PUBLISHED,
       EXPIRED or HIDDEN. You should the property :attr:`calculated_status` if
       you want that the dates are taken in account.

    .. attribute:: template
       A string containing the name of the template file for this page.
    """

    # some class constants to refer to, e.g. Page.DRAFT
    DRAFT = 0
    PUBLISHED = 1
    EXPIRED = 2
    HIDDEN = 3
    STATUSES = (
        (PUBLISHED, _('Published')),
        (HIDDEN, _('Hidden')),
        (DRAFT, _('Draft')),
    )

    PAGE_LANGUAGES_KEY = "page_%d_languages"
    PAGE_URL_KEY = "page_%d_url"
    ANCESTORS_KEY = 'ancestors_%d'
    CHILDREN_KEY = 'children_%d'
    PUB_CHILDREN_KEY = 'pub_children_%d'

    # used to identify pages across different databases
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    author = models.ForeignKey(django_settings.AUTH_USER_MODEL,
            verbose_name=_('author'))

    parent = models.ForeignKey('self', null=True, blank=True,
            related_name='children', verbose_name=_('parent'))
    creation_date = models.DateTimeField(_('creation date'), editable=False,
            default=get_now)
    publication_date = models.DateTimeField(_('publication date'),
            null=True, blank=True, help_text=_('''When the page should go
            live. Status must be "Published" for page to go live.'''))
    publication_end_date = models.DateTimeField(_('publication end date'),
            null=True, blank=True, help_text=_('''When to expire the page.
            Leave empty to never expire.'''))

    last_modification_date = models.DateTimeField(_('last modification date'))

    status = models.IntegerField(_('status'), choices=STATUSES, default=DRAFT)
    template = models.CharField(_('template'), max_length=100, null=True,
            blank=True)

    delegate_to = models.CharField(_('delegate to'), max_length=100, null=True,
            blank=True)

    freeze_date = models.DateTimeField(_('freeze date'),
            null=True, blank=True, help_text=_('''Don't publish any content
            after this date.'''))

    if settings.PAGE_USE_SITE_ID:
        sites = models.ManyToManyField(Site,
            default=[global_settings.SITE_ID],
            help_text=_('The site(s) the page is accessible at.'),
            verbose_name=_('sites'))

    redirect_to_url = models.CharField(_('redirect to url'), max_length=200, null=True, blank=True)

    redirect_to = models.ForeignKey('self', null=True, blank=True,
        related_name='redirected_pages', verbose_name=_('redirect to'))

    # Managers
    objects = PageManager()

    if settings.PAGE_TAGGING:
        tags = settings.PAGE_TAGGING_FIELD()

    class Meta:
        """Make sure the default page ordering is correct."""
        ordering = ['tree_id', 'lft']
        get_latest_by = "publication_date"
        verbose_name = _('page')
        verbose_name_plural = _('pages')
        permissions = settings.PAGE_EXTRA_PERMISSIONS

    def __init__(self, *args, **kwargs):
        """Instanciate the page object."""
        # per instance cache
        self._languages = None
        self._content_dict = None
        self._is_first_root = None
        self._complete_slug = None
        super(Page, self).__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        """Override the default ``save`` method."""
        if not self.status:
            self.status = self.DRAFT
        # Published pages should always have a publication date
        if self.publication_date is None and self.status == self.PUBLISHED:
            self.publication_date = get_now()
        # Drafts should not, unless they have been set to the future
        if self.status == self.DRAFT:
            if settings.PAGE_SHOW_START_DATE:
                if (self.publication_date and
                        self.publication_date <= get_now()):
                    self.publication_date = None
            else:
                self.publication_date = None
        self.last_modification_date = get_now()
        super(Page, self).save(*args, **kwargs)
        # fix sites many-to-many link when the're hidden from the form
        if settings.PAGE_HIDE_SITES and self.sites.count() == 0:
            self.sites.add(Site.objects.get(pk=global_settings.SITE_ID))

    def _get_calculated_status(self):
        """Get the calculated status of the page based on
        :attr:`Page.publication_date`,
        :attr:`Page.publication_end_date`,
        and :attr:`Page.status`."""
        if settings.PAGE_SHOW_START_DATE and self.publication_date:
            if self.publication_date > get_now():
                return self.DRAFT

        if settings.PAGE_SHOW_END_DATE and self.publication_end_date:
            if self.publication_end_date < get_now():
                return self.EXPIRED

        return self.status
    calculated_status = property(_get_calculated_status)

    def _visible(self):
        """Return True if the page is visible on the frontend."""
        return self.calculated_status in (self.PUBLISHED, self.HIDDEN)
    visible = property(_visible)

    def get_children(self):
        """Cache superclass result"""
        key = self.CHILDREN_KEY % self.id
        #children = cache.get(key, None)
        # if children is None:
        children = super(Page, self).get_children()
        #cache.set(key, children)
        return children

    def published_children(self):
        """Return a :class:`QuerySet` of published children page"""
        key = self.PUB_CHILDREN_KEY % self.id
        #children = cache.get(key, None)
        # if children is None:
        children = Page.objects.filter_published(self.get_children()).all()
        #cache.set(key, children)
        return children

    def get_children_for_frontend(self):
        """Return a :class:`QuerySet` of published children page"""
        return self.published_children()

    def get_date_ordered_children_for_frontend(self):
        """Return a :class:`QuerySet` of published children page ordered
        by publication date."""
        return self.published_children().order_by('-publication_date')

    def move_to(self, target, position='first-child'):
        """Invalidate cache when moving"""

        # Invalidate both in case position matters,
        # otherwise only target is needed.
        self.invalidate()
        target.invalidate()
        super(Page, self).move_to(target, position=position)

    def invalidate(self):
        """Invalidate cached data for this page."""

        cache.delete(self.PAGE_LANGUAGES_KEY % (self.id))
        cache.delete('PAGE_FIRST_ROOT_ID')
        cache.delete(self.CHILDREN_KEY % self.id)
        cache.delete(self.PUB_CHILDREN_KEY % self.id)
        # XXX: Should this have a depth limit?
        if self.parent_id:
            self.parent.invalidate()
        self._languages = None
        self._complete_slug = None
        self._content_dict = dict()

        placeholders = get_placeholders(self.get_template())

        p_names = [p.ctype for p in placeholders]
        if 'slug' not in p_names:
            p_names.append('slug')
        if 'title' not in p_names:
            p_names.append('title')

        from pages.managers import fake_page
        shared = [p for p in placeholders if p.shared]
        for share in shared:
            fake_page.invalidate(share.ctype)

        # delete content cache, frozen or not
        for name in p_names:
            # frozen
            cache.delete(
                PAGE_CONTENT_DICT_KEY %
                (self.id, name, 1))
            # not frozen
            cache.delete(
                PAGE_CONTENT_DICT_KEY %
                (self.id, name, 0))

        cache.delete(self.PAGE_URL_KEY % (self.id))

    def get_languages(self):
        """
        Return a list of all used languages for this page.
        """
        if self._languages:
            return self._languages
        self._languages = cache.get(self.PAGE_LANGUAGES_KEY % (self.id))
        if self._languages is not None:
            return self._languages

        languages = [c['language'] for
            c in Content.objects.filter(page=self,
            type="slug").values('language')]
        # remove duplicates
        languages = sorted(set(languages))
        cache.set(self.PAGE_LANGUAGES_KEY % (self.id), languages)
        self._languages = languages
        return languages

    def is_first_root(self):
        """Return ``True`` if this page is the first root pages."""
        parent_cache_key = 'PARENT_FOR_%d' % self.id
        has_parent = cache.get(parent_cache_key, None)
        if has_parent is None:
            has_parent = not not self.parent
            cache.set(parent_cache_key, has_parent)

        if has_parent:
            return False
        if self._is_first_root is not None:
            return self._is_first_root
        first_root_id = cache.get('PAGE_FIRST_ROOT_ID')
        if first_root_id is not None:
            self._is_first_root = first_root_id == self.id
            return self._is_first_root
        try:
            first_root_id = Page.objects.root().values('id')[0]['id']
        except IndexError:
            first_root_id = None
        if first_root_id is not None:
            cache.set('PAGE_FIRST_ROOT_ID', first_root_id)
        self._is_first_root = self.id == first_root_id
        return self._is_first_root

    def get_template(self):
        """
        Get the :attr:`template <Page.template>` of this page if
        defined or the closer parent's one if defined
        or :attr:`pages.settings.PAGE_DEFAULT_TEMPLATE` otherwise.
        """
        if self.template:
            return self.template

        template = None
        for p in self.get_ancestors(ascending=True):
            if p.template:
                template = p.template
                break

        if not template:
            template = settings.PAGE_DEFAULT_TEMPLATE

        return template

    def get_template_name(self):
        """
        Get the template name of this page if defined or if a closer
        parent has a defined template or
        :data:`pages.settings.PAGE_DEFAULT_TEMPLATE` otherwise.
        """
        template = self.get_template()
        page_templates = settings.get_page_templates()
        for t in page_templates:
            if t[0] == template:
                return t[1]
        return template

    def valid_targets(self):
        """Return a :class:`QuerySet` of valid targets for moving a page
        into the tree.

        :param perms: the level of permission of the concerned user.
        """
        exclude_list = [self.id]
        for p in self.get_descendants():
            exclude_list.append(p.id)
        return Page.objects.exclude(id__in=exclude_list)

    # Content methods

    def get_content(self, language, ctype, language_fallback=False):
        """Shortcut method for retrieving a piece of page content

        :param language: wanted language, if not defined default is used.
        :param ctype: the type of content.
        :param fallback: if ``True``, the content will also be searched in \
        other languages.
        """
        return Content.objects.get_content(self, language, ctype,
            language_fallback)

    def expose_content(self):
        """Return all the current content of this page into a `string`.

        This is used by the haystack framework to build the search index."""
        placeholders = get_placeholders(self.get_template())
        exposed_content = []
        for lang in self.get_languages():
            for p in placeholders:
                content = self.get_content(lang, p.ctype, False)
                if content:
                    exposed_content.append(content)
        return "\r\n".join(exposed_content)

    def content_by_language(self, language):
        """
        Return a list of latest published
        :class:`Content <pages.models.Content>`
        for a particluar language.

        :param language: wanted language,
        """
        placeholders = get_placeholders(self.get_template())
        content_list = []
        for p in placeholders:
            try:
                content = Content.objects.get_content_object(self,
                    language, p.ctype)
                content_list.append(content)
            except Content.DoesNotExist:
                pass
        return content_list

    ### Title and slug

    def get_url_path(self, language=None):
        """Return the URL's path component. Add the language prefix if
        ``PAGE_USE_LANGUAGE_PREFIX`` setting is set to ``True``.

        :param language: the wanted url language.
        """
        if self.is_first_root():
            # this is used to allow users to change URL of the root
            # page. The language prefix is not usable here.
            try:
                return reverse('pages-root')
            except Exception:
                pass
        url = self.get_complete_slug(language)
        if not language:
            language = settings.PAGE_DEFAULT_LANGUAGE
        if settings.PAGE_USE_LANGUAGE_PREFIX:
            return reverse('pages-details-by-path',
                args=[language, url])
        else:
            return reverse('pages-details-by-path', args=[url])

    def get_absolute_url(self, language=None):
        """Alias for `get_url_path`.

        :param language: the wanted url language.
        """
        return self.get_url_path(language=language)

    def get_complete_slug(self, language=None, hideroot=True):
        """Return the complete slug of this page by concatenating
        all parent's slugs.

        :param language: the wanted slug language."""
        if not language:
            language = settings.PAGE_DEFAULT_LANGUAGE

        if self._complete_slug and language in self._complete_slug:
            return self._complete_slug[language]

        self._complete_slug = cache.get(self.PAGE_URL_KEY % (self.id))
        if self._complete_slug is None:
            self._complete_slug = {}
        elif language in self._complete_slug:
            return self._complete_slug[language]

        if hideroot and settings.PAGE_HIDE_ROOT_SLUG and self.is_first_root():
            url = ''
        else:
            url = '%s' % self.slug(language)

        key = self.ANCESTORS_KEY % self.id
        ancestors = cache.get(key, None)
        if ancestors is None:
            ancestors = self.get_ancestors(ascending=True)
            cache.set(key, ancestors)

        for ancestor in ancestors:
            url = ancestor.slug(language) + '/' + url

        self._complete_slug[language] = url
        cache.set(self.PAGE_URL_KEY % (self.id), self._complete_slug)
        return url

    def slug_with_level(self, language=None):
        """Display the slug of the page prepended with insecable
        spaces to simluate the level of page in the hierarchy."""
        level = ''
        if self.level:
            for n in range(0, self.level):
                level += '&nbsp;&nbsp;&nbsp;'
        return mark_safe(level + self.slug(language))

    def slug(self, language=None, fallback=True):
        """
        Return the slug of the page depending on the given language.

        :param language: wanted language, if not defined default is used.
        :param fallback: if ``True``, the slug will also be searched in other \
        languages.
        """

        slug = self.get_content(language, 'slug', language_fallback=fallback)
        if slug == '':
            return "Page {0}".format(self.id)

        return slug

    def title(self, language=None, fallback=True):
        """
        Return the title of the page depending on the given language.

        :param language: wanted language, if not defined default is used.
        :param fallback: if ``True``, the slug will also be searched in \
        other languages.
        """
        if not language:
            language = settings.PAGE_DEFAULT_LANGUAGE

        return self.get_content(language, 'title', language_fallback=fallback)

    # Formating methods

    def margin_level(self):
        """Used in the admin menu to create the left margin."""
        return self.level * 2

    def __str__(self):
        """Representation of the page, saved or not."""
        if self.id:
            # without ID a slug cannot be retrieved
            return self.slug()
        return "Page without id"


@python_2_unicode_compatible
class Content(models.Model):
    """A block of content, tied to a :class:`Page <pages.models.Page>`,
    for a particular language"""

    # languages could have five characters : Brazilian Portuguese is pt-br
    language = models.CharField(_('language'), max_length=5, blank=False)
    body = models.TextField(_('body'), blank=True)
    type = models.CharField(
        _('type'), max_length=100, blank=False,
        db_index=True)
    page = models.ForeignKey(Page, verbose_name=_('page'), null=True)

    creation_date = models.DateTimeField(
        _('creation date'), editable=False,
        default=get_now)
    objects = ContentManager()

    class Meta:
        get_latest_by = 'creation_date'
        verbose_name = _('content')
        verbose_name_plural = _('contents')

    def __str__(self):
        return u"{0} :: {1}".format(self.page.slug(), self.body[0:15])


@python_2_unicode_compatible
class PageAlias(models.Model):
    """URL alias for a :class:`Page <pages.models.Page>`"""
    page = models.ForeignKey(Page, null=True, blank=True,
        verbose_name=_('page'))
    url = models.CharField(max_length=255, unique=True)
    objects = PageAliasManager()

    class Meta:
        verbose_name_plural = _('Aliases')

    def save(self, *args, **kwargs):
        # normalize url
        self.url = normalize_url(self.url)
        super(PageAlias, self).save(*args, **kwargs)

    def __str__(self):
        return "{0} :: {1}".format(self.url, self.page.get_complete_slug())


def media_filename(instance, filename):
    avoid_collision = uuid.uuid4().hex[:8]
    name_parts = filename.split('.')
    if len(name_parts) > 1:
        name = slugify('.'.join(name_parts[:-1]), allow_unicode=True)
        ext = slugify(name_parts[-1])
        name = name + '.' + ext
    else:
        name = slugify(data.name)
    filename = os.path.join(
        settings.PAGE_UPLOAD_ROOT,
        'medias',
        name
    )
    return filename


@python_2_unicode_compatible
class Media(models.Model):
    """Media model :class:`Media <pages.models.Media>`"""
    title = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    url = models.FileField(upload_to=media_filename)
    extension = models.CharField(max_length=32, blank=True, editable=False)
    creation_date = models.DateTimeField(_('creation date'), editable=False,
            default=get_now)

    def image(self):
        if self.extension in ['png', 'jpg', 'jpeg']:
            return u'<img width="60" src="%s" />' % os.path.join(
                settings.PAGES_MEDIA_URL, self.url.name)
        if self.extension == 'pdf':
            return u'<i class="fa fa-file-pdf-o" aria-hidden="true"></i>'
        if self.extension in ['doc', 'docx']:
            return u'<i class="fa fa-file-word-o" aria-hidden="true"></i>'
        if self.extension in ['zip', 'gzip', 'rar']:
            return u'<i class="fa fa-file-archive-o" aria-hidden="true"></i>    '
        return u'<i class="fa fa-file-o" aria-hidden="true"></i>'
    image.short_description = _('Thumbnail')
    image.allow_tags = True

    class Meta:
        verbose_name_plural = _('Medias')

    def save(self, *args, **kwargs):
        parts = self.url.name.split('.')
        if len(parts) > 1:
            self.extension = parts[-1].lower()
        if not self.title:
            parts = self.url.name.split('/')
            self.title = parts[-1]

        super(Media, self).save(*args, **kwargs)

    def __str__(self):
        return self.url.name
