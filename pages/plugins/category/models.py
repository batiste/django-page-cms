# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django import forms

from pages.cache import cache
from pages.models import Page
from pages.widgets_registry import register_widget


class Category(models.Model):
    """To categorize :class:`Page <pages.models.Page>` objects
    There is no direct foreign key, this is handled by placeholders
    """

    PAGES_KEY = 'pages_%d'

    # languages could have five characters : Brazilian Portuguese is pt-br
    language = models.CharField(_('language'), max_length=5, blank=False)

    title = models.CharField(_('Title'), max_length=255)
    slug = models.CharField(_('Slug'), max_length=255)

    class Meta:
        # it's not possible to have south migrations
        # in the plugin if the app_label is the same
        # app_label = 'pages'
        verbose_name_plural = _('categories')

    def __unicode__(self):
        return self.title

    def get_pages(self):
        """Cache the pages we have"""
        key = self.PAGES_KEY % self.id
        pages = cache.get(key, None)
        if pages is None:
            pages = Page.objects.filter(content__language=self.language,
                    content__type='category', content__body=self.slug)
            cache.set(key, pages)
        return pages


class CategoryWidget(forms.Select):
    """Can use Categories through placeholders"""
    def __init__(self, attrs=None, language=None, **kwargs):
        choices = kwargs.pop('choices', ())
        choices = list(choices)
        cats = Category.objects.all()
        if language:
            cats = cats.filter(language=language)
        choices.extend((cat.slug, cat.title) for cat in cats)
        super(CategoryWidget, self).__init__(attrs=attrs, choices=choices)


register_widget(CategoryWidget)