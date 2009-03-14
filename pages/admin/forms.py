# -*- coding: utf-8 -*-
from django import forms
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _

from pages import settings
from pages.models import Page, Content

class PageForm(forms.ModelForm):
    title = forms.CharField(
        label=_('Title'),
        widget=forms.TextInput(),
        help_text=_('The default title')
    )
    slug = forms.CharField(
        label=_('Slug'),
        widget=forms.TextInput(),
        help_text=_('The part of the title that is used in permalinks')
    )
    language = forms.ChoiceField(
        label=_('Language'),
        choices=settings.PAGE_LANGUAGES,
        help_text=_('The current language of the content fields.'),
    )
    template = forms.ChoiceField(
        required=False,
        label=_('Template'),
        choices=settings.PAGE_TEMPLATES,
        help_text=_('The template used to render the content.')
    )
    
    target = forms.IntegerField(required=False)
    position = forms.CharField(required=False)
    
    if settings.PAGE_TAGGING:
        from tagging.forms import TagField
        from pages.admin.widgets import AutoCompleteTagInput
        tags = TagField(widget=AutoCompleteTagInput(), required=False)

    class Meta:
        model = Page

    def clean_slug(self):
        
        slug = slugify(self.cleaned_data['slug'])
        target = self.data.get('target', None)
        position = self.data.get('position', None)
        
        if settings.PAGE_UNIQUE_SLUG_REQUIRED:
            if self.instance.id:
                if Content.objects.exclude(page=self.instance).filter(body=slug, type="slug").count():
                    raise forms.ValidationError(_('Another page with this slug already exists'))
            elif Content.objects.filter(body=slug, type="slug").count():
                raise forms.ValidationError(_('Another page with this slug already exists'))

        if not settings.PAGE_UNIQUE_SLUG_REQUIRED:
            if target and position:
                try:
                    target = Page.objects.get(pk=target)
                except Page.DoesNotExist:
                    if slug in [sibling.slug() for sibling in Page.objects.root()]:
                        raise forms.ValidationError(_('A sibiling with this slug already exists at the root level'))
                else:
                    if position in ['right-sibling', 'left-sibling']:
                        if slug in [sibling.slug() for sibling in target.get_siblings()]:
                            raise forms.ValidationError(_('A sibiling with this slug already exists at the targeted position'))
                    if position == 'first-child':
                        if slug in [sibling.slug() for sibling in target.get_children()]:
                            raise forms.ValidationError(_('A children with this slug already exists at the targeted position'))
            else:
                if self.instance.id:
                    if slug in [sibling.slug() for sibling in self.instance.get_siblings().exclude(id=self.instance.id)]:
                        raise forms.ValidationError(_('A sibiling with this slug already exists'))
                else:
                    if slug in [sibling.slug() for sibling in Page.objects.root()]:
                        raise forms.ValidationError(_('A sibiling with this slug already exists at the root level'))
            
        return slug
