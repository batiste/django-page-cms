# -*- coding: utf-8 -*-
"""Page CMS forms"""
from django import forms
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _

from pages import settings
from pages.models import Page, Content
from pages.urlconf_registry import get_choices
from pages.widgets import LanguageChoiceWidget

# error messages
another_page_error = _('Another page with this slug already exists')
sibling_position_error = _('A sibling with this slug already exists at the \
targeted position')
child_error = _('A child with this slug already exists at the targeted \
position')
sibling_error = _('A sibling with this slug already exists')
sibling_root_error = _('A sibling with this slug already exists at the root \
level')

class PageForm(forms.ModelForm):
    """Form for page creation"""
    
    title = forms.CharField(
        label=_('Title'),
        widget=forms.TextInput(),
    )
    slug = forms.CharField(
        label=_('Slug'),
        widget=forms.TextInput(),
        help_text=_('The slug will be used to create the page URL, \
it must be unique among the other pages of the same level.')
    )
    language = forms.ChoiceField(
        label=_('Language'),
        choices=settings.PAGE_LANGUAGES,
        widget=LanguageChoiceWidget()
    )
    template = forms.ChoiceField(
        required=False,
        label=_('Template'),
        choices=settings.get_page_templates(),
    )
    delegate_to = forms.ChoiceField(
        required=False,
        label=_('Delegate to application'),
        choices=get_choices(),
    )
    freeze_date = forms.DateTimeField(
        required=False,
        label=_('Freeze'),
        help_text=_("Don't publish any content after this date. Format is 'Y-m-d H:M:S'")
        # those make tests fail miserably
        #widget=widgets.AdminSplitDateTime()
        #widget=widgets.AdminTimeWidget()
    )
    
    target = forms.IntegerField(required=False, widget=forms.HiddenInput)
    position = forms.CharField(required=False, widget=forms.HiddenInput)
    
    if settings.PAGE_TAGGING:
        from tagging.forms import TagField
        from pages.widgets import AutoCompleteTagInput
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
                if Content.objects.exclude(page=self.instance).filter(
                    body=slug, type="slug").count():
                    raise forms.ValidationError(another_page_error)
            elif Content.objects.filter(body=slug, type="slug").count():
                raise forms.ValidationError(another_page_error)

        if settings.PAGE_USE_SITE_ID:
            if settings.PAGE_HIDE_SITES:
                site_ids = [settings.SITE_ID]
            else:
                site_ids = [int(x) for x in self.data.getlist('sites')]
            def intersects_sites(sibling):
                return sibling.sites.filter(id__in=site_ids).count() > 0
        else:
            def intersects_sites(sibling):
                return True

        if not settings.PAGE_UNIQUE_SLUG_REQUIRED:
            if target and position:
                target = Page.objects.get(pk=target)
                if position in ['right', 'left']:
                    slugs = [sibling.slug() for sibling in
                             target.get_siblings() 
                             if intersects_sites(sibling)]
                    slugs.append(target.slug())
                    if slug in slugs:
                        raise forms.ValidationError(sibling_position_error)
                if position == 'first-child':
                    if slug in [sibling.slug() for sibling in
                                target.get_children()
                                if intersects_sites(sibling)]:
                        raise forms.ValidationError(child_error)
            else:
                if self.instance.id:
                    if (slug in [sibling.slug() for sibling in
                        self.instance.get_siblings().exclude(
                            id=self.instance.id
                        ) if intersects_sites(sibling)]):
                        raise forms.ValidationError(sibling_error)
                else:
                    if slug in [sibling.slug() for sibling in
                                Page.objects.root()
                                if intersects_sites(sibling)]:
                        raise forms.ValidationError(sibling_root_error)
        return slug
