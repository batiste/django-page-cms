"""Django page CMS ``models``."""

from pages.utils import get_placeholders, normalize_url, now_utc
from pages.managers import PageManager, ContentManager
from pages.managers import PageAliasManager, ISODATE_FORMAT
from pages import settings

from datetime import datetime
from django.db import models
from django.contrib.auth.models import User, SiteProfileNotAvailable
from django.db.models import Max
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.sites.models import Site
from django.conf import settings as global_settings


from mptt.models import MPTTModel
if settings.PAGE_TAGGING:
    from taggit.managers import TaggableManager

PAGE_CONTENT_DICT_KEY = ContentManager.PAGE_CONTENT_DICT_KEY


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
    PAGE_BROKEN_LINK_KEY = "page_broken_link_%s"

    author = models.ForeignKey(User, verbose_name=_('author'))

    parent = models.ForeignKey('self', null=True, blank=True,
            related_name='children', verbose_name=_('parent'))
    creation_date = models.DateTimeField(_('creation date'), editable=False,
            default=now_utc)
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
                default=lambda: [global_settings.SITE_ID],
                help_text=_('The site(s) the page is accessible at.'),
                verbose_name=_('sites'))

    redirect_to_url = models.CharField(max_length=200, null=True, blank=True)

    redirect_to = models.ForeignKey('self', null=True, blank=True,
            related_name='redirected_pages')

    # Managers
    objects = PageManager()

    if settings.PAGE_TAGGING:
        tags = TaggableManager(blank=True)

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
        self._complete_slug = None
        self._content_dict = None
        self._is_first_root = None
        super(Page, self).__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        """Override the default ``save`` method."""
        if not self.status:
            self.status = self.DRAFT
        # Published pages should always have a publication date
        if self.publication_date is None and self.status == self.PUBLISHED:
            self.publication_date = now_utc()
        # Drafts should not, unless they have been set to the future
        if self.status == self.DRAFT:
            if settings.PAGE_SHOW_START_DATE:
                if (self.publication_date and
                        self.publication_date <= now_utc()):
                    self.publication_date = None
            else:
                self.publication_date = None
        self.last_modification_date = now_utc()
        # let's assume there is no more broken links after a save
        cache.delete(self.PAGE_BROKEN_LINK_KEY % self.id)
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
            if self.publication_date > now_utc():
                return self.DRAFT

        if settings.PAGE_SHOW_END_DATE and self.publication_end_date:
            if self.publication_end_date < now_utc():
                return self.EXPIRED

        return self.status
    calculated_status = property(_get_calculated_status)

    def _visible(self):
        """Return True if the page is visible on the frontend."""
        return self.calculated_status in (self.PUBLISHED, self.HIDDEN)
    visible = property(_visible)

    def get_children_for_frontend(self):
        """Return a :class:`QuerySet` of published children page"""
        return Page.objects.filter_published(self.get_children())

    def get_date_ordered_children_for_frontend(self):
        """Return a :class:`QuerySet` of published children page ordered
        by publication date."""
        return self.get_children_for_frontend().order_by('-publication_date')

    def invalidate(self):
        """Invalidate cached data for this page."""

        cache.delete(self.PAGE_LANGUAGES_KEY % (self.id))
        cache.delete('PAGE_FIRST_ROOT_ID')
        self._languages = None
        self._complete_slug = None
        self._content_dict = dict()

        p_names = [p.name for p in get_placeholders(self.get_template())]
        if 'slug' not in p_names:
            p_names.append('slug')
        if 'title' not in p_names:
            p_names.append('title')
        # delete content cache, frozen or not
        for name in p_names:
            # frozen
            cache.delete(PAGE_CONTENT_DICT_KEY %
                (self.id, name, 1))
            # not frozen
            cache.delete(PAGE_CONTENT_DICT_KEY %
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
        languages = list(set(languages))
        languages.sort()
        cache.set(self.PAGE_LANGUAGES_KEY % (self.id), languages)
        self._languages = languages
        return languages

    def is_first_root(self):
        """Return ``True`` if this page is the first root pages."""
        if self.parent:
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

        This method is only there for backward compatibility and will be
        removed in a near futur.

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
            url = u''
        else:
            url = u'%s' % self.slug(language)
        for ancestor in self.get_ancestors(ascending=True):
            url = ancestor.slug(language) + u'/' + url

        self._complete_slug[language] = url
        cache.set(self.PAGE_URL_KEY % (self.id), self._complete_slug)
        return url

    def get_url(self, language=None):
        """Alias for `get_complete_slug`.

        This method is only there for backward compatibility and will be
        removed in a near futur.

        :param language: the wanted url language.
        """
        return self.get_complete_slug(language=language)

    def slug(self, language=None, fallback=True):
        """
        Return the slug of the page depending on the given language.

        :param language: wanted language, if not defined default is used.
        :param fallback: if ``True``, the slug will also be searched in other \
        languages.
        """

        slug = self.get_content(language, 'slug', language_fallback=fallback)

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
            for ctype in [p.name for p in placeholders]:
                content = self.get_content(lang, ctype, False)
                if content:
                    exposed_content.append(content)
        return u"\r\n".join(exposed_content)

    def content_by_language(self, language):
        """
        Return a list of latest published
        :class:`Content <pages.models.Content>`
        for a particluar language.

        :param language: wanted language,
        """
        placeholders = get_placeholders(self.get_template())
        content_list = []
        for ctype in [p.name for p in placeholders]:
            try:
                content = Content.objects.get_content_object(self,
                    language, ctype)
                content_list.append(content)
            except Content.DoesNotExist:
                pass
        return content_list

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

    def has_broken_link(self):
        """
        Return ``True`` if the page have broken links to other pages
        into the content.
        """
        return cache.get(self.PAGE_BROKEN_LINK_KEY % self.id)

    def valid_targets(self):
        """Return a :class:`QuerySet` of valid targets for moving a page
        into the tree.

        :param perms: the level of permission of the concerned user.
        """
        exclude_list = [self.id]
        for p in self.get_descendants():
            exclude_list.append(p.id)
        return Page.objects.exclude(id__in=exclude_list)

    def slug_with_level(self, language=None):
        """Display the slug of the page prepended with insecable
        spaces equal to simluate the level of page in the hierarchy."""
        level = ''
        if self.level:
            for n in range(0, self.level):
                level += '&nbsp;&nbsp;&nbsp;'
        return mark_safe(level + self.slug(language))

    def margin_level(self):
        """Used in the admin menu to create the left margin."""
        return self.level * 2

    def dump_json_data(self):
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
            params = {'page': self}
            if self.freeze_date:
                params['creation_date__lte'] = self.freeze_date
            cqs = Content.objects.filter(**params)
            cqs = cqs.values('language').annotate(latest=Max('creation_date'))
            return [c['language'] for c in cqs.order_by('latest')]
        languages = content_langs_ordered()

        def language_content(ctype):
            return dict(
                (lang, self.get_content(lang, ctype, language_fallback=False))
                for lang in languages)

        def placeholder_content():
            """Return content of each placeholder in each language."""
            out = {}
            for p in get_placeholders(self.get_template()):
                if p.name in ('title', 'slug'):
                    continue # these were already included
                out[p.name] = language_content(p.name)
            return out

        def isoformat(d):
            return None if d is None else d.strftime(ISODATE_FORMAT)

        def custom_email(user):
            """Allow a user's profile to return an email for the user."""
            try:
                profile = user.get_profile()
            except (SiteProfileNotAvailable, ObjectDoesNotExist):
                return user.email
            get_email = getattr(profile, 'get_email', None)
            return get_email() if get_email else user.email

        return {
            'complete_slug': dict(
                (lang, self.get_complete_slug(lang, hideroot=False))
                for lang in languages),
            'title': language_content('title'),
            'author_email': custom_email(self.author),
            'creation_date': isoformat(self.creation_date),
            'publication_date': isoformat(self.publication_date),
            'publication_end_date': isoformat(self.publication_end_date),
            'last_modification_date': isoformat(self.last_modification_date),
            'status': {
                Page.PUBLISHED: 'published',
                Page.HIDDEN: 'hidden',
                Page.DRAFT: 'draft'}[self.status],
            'template': self.template,
            'sites': (
                [site.domain for site in self.sites.all()]
                if settings.PAGE_USE_SITE_ID else []),
            'redirect_to_url': self.redirect_to_url,
            'redirect_to_complete_slug': dict(
                (lang, self.redirect_to.get_complete_slug(
                    lang, hideroot=False))
                for lang in self.redirect_to.get_languages()
                ) if self.redirect_to is not None else None,
            'content': placeholder_content(),
            'content_language_updated_order': languages,
        }

    def update_redirect_to_from_json(self, redirect_to_complete_slugs):
        """
        The second pass of PageManager.create_and_update_from_json_data
        used to update the redirect_to field.

        Returns a messages list to be appended to the messages from the
        first pass.
        """
        messages = []
        s = ''
        for lang, s in redirect_to_complete_slugs.items():
            r = Page.objects.from_path(s, lang, exclude_drafts=False)
            if r:
                self.redirect_to = r
                self.save()
                break
        else:
            messages.append(_("Could not find page for redirect-to field"
                " '%s'") % (s,))
        return messages

    def __unicode__(self):
        """Representation of the page, saved or not."""
        if self.id:
            # without ID a slug cannot be retrieved
            slug = self.slug()
            if slug:
                return slug
            return u"Page %d" % self.id
        return u"Page without id"


class Content(models.Model):
    """A block of content, tied to a :class:`Page <pages.models.Page>`,
    for a particular language"""

    # languages could have five characters : Brazilian Portuguese is pt-br
    language = models.CharField(_('language'), max_length=5, blank=False)
    body = models.TextField(_('body'))
    type = models.CharField(_('type'), max_length=100, blank=False,
        db_index=True)
    page = models.ForeignKey(Page, verbose_name=_('page'))

    creation_date = models.DateTimeField(_('creation date'), editable=False,
        default=now_utc)
    objects = ContentManager()

    class Meta:
        get_latest_by = 'creation_date'
        verbose_name = _('content')
        verbose_name_plural = _('contents')

    def __unicode__(self):
        return u"%s :: %s" % (self.page.slug(), self.body[0:15])


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

    def __unicode__(self):
        return u"%s :: %s" % (self.url, self.page.get_complete_slug())
