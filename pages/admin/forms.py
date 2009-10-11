# -*- coding: utf-8 -*-
"""Page CMS forms"""
from django import forms
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _

from pages import settings
from pages.models import Page, Content

class PageForm(forms.ModelForm):
    """Form for page creation"""
    title = forms.CharField(
        label=_('Title'),
        widget=forms.TextInput(),
    )
    slug = forms.CharField(
        label=_('Slug'),
        widget=forms.TextInput(),
        help_text=_('The slug will be used to create the page URL, it must be unique among the other pages of the same level.')
    )
    language = forms.ChoiceField(
        label=_('Language'),
        choices=settings.PAGE_LANGUAGES,
    )
    template = forms.ChoiceField(
        required=False,
        label=_('Template'),
        choices=settings.PAGE_TEMPLATES,
    )
    
    target = forms.IntegerField(required=False, widget=forms.HiddenInput)
    position = forms.CharField(required=False, widget=forms.HiddenInput)
    
    if settings.PAGE_TAGGING:
        from tagging.forms import TagField
        from pages.admin.widgets import AutoCompleteTagInput
        tags = TagField(widget=AutoCompleteTagInput(), required=False)

    class Meta:
        model = Page

    def clean_slug(self):
        """Handle move action on the pages"""
        
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
                target = Page.objects.get(pk=target)
                if position in ['right', 'left']:
                    slugs = [sibling.slug() for sibling in target.get_siblings()]
                    slugs.append(target.slug())
                    if slug in slugs:
                        raise forms.ValidationError(
                            _('A sibiling with this slug already exists at the targeted position'))
                if position == 'first-child':
                    if slug in [sibling.slug() for sibling in target.get_children()]:
                        raise forms.ValidationError(
                            _('A child with this slug already exists at the targeted position'))
            else:
                if self.instance.id:
                    if (slug in [sibling.slug() for sibling in
                        self.instance.get_siblings().exclude(id=self.instance.id)]):
                        raise forms.ValidationError(
                            _('A sibiling with this slug already exists'))
                else:
                    if slug in [sibling.slug() for sibling in Page.objects.root()]:
                        raise forms.ValidationError(
                            _('A sibiling with this slug already exists at the root level'))
        return slug
