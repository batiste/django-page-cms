# -*- coding: utf-8 -*-
"""Page CMS forms"""
from django import forms
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _
from django.conf import settings as global_settings

from pages import settings
from pages.models import Page, Content

from pages.urlconf_registry import get_choices
from pages.widgets import LanguageChoiceWidget
import collections

error_dict = {
    'another_page_error': _('Another page with this slug already exists'),
    'sibling_position_error': _('A sibling with this slug already exists at the targeted position'),
    'child_error': _('A child with this slug already exists at the targeted position'),
    'sibling_error': _('A sibling with this slug already exists'),
    'sibling_root_error': _('A sibling with this slug already exists at the root level'),
}

def automatic_slug_renaming(slug, is_slug_safe):
    """Helper to add numbers to slugs"""

    if not isinstance(is_slug_safe, collections.Callable):
        raise TypeError('is_slug_safe must be callable')

    if is_slug_safe(slug):
       return slug

    count = 2
    new_slug = slug + "-" + str(count)
    while not is_slug_safe(new_slug):
        count = count + 1
        new_slug = slug + "-" + str(count)
    return new_slug

def unique_slug_required(form, slug):
    """Enforce a unique slug accross all pages and websistes."""

    if hasattr(form, 'instance') and form.instance.id:
        if Content.objects.exclude(page=form.instance).filter(
            body=slug, type="slug").count():
            raise forms.ValidationError(error_dict['another_page_error'])
    elif Content.objects.filter(body=slug, type="slug").count():
        raise forms.ValidationError(error_dict['another_page_error'])
    return slug

def intersect_sites_method(form):
    """Return a method to intersect sites."""
    if settings.PAGE_USE_SITE_ID:
        if settings.PAGE_HIDE_SITES:
            site_ids = [global_settings.SITE_ID]
        else:
            site_ids = [int(x) for x in form.data.getlist('sites')]
        def intersects_sites(sibling):
            return sibling.sites.filter(id__in=site_ids).count() > 0
    else:
        def intersects_sites(sibling):
            return True
    return intersects_sites

def make_form(model_, placeholders):

    # a new form is needed every single time as some
    # initial data are bound
    class PageForm(forms.ModelForm):
        """Form for page creation"""

        def __init__(self, *args, **kwargs):
            super(PageForm, self).__init__(*args, **kwargs)
            for p in placeholders:
                if not self.fields[p.ctype]:
                    self.fields[p.ctype] = forms.TextField()

        target = forms.IntegerField(required=False, widget=forms.HiddenInput)
        position = forms.CharField(required=False, widget=forms.HiddenInput)

        class Meta:
            model = model_
            exclude = ('author', 'last_modification_date', 'parent')

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

        def clean_slug(self):
            """Handle move action on the pages"""

            slug = slugify(self.cleaned_data['slug'])
            target = self.data.get('target', None)
            position = self.data.get('position', None)

            # this enforce a unique slug for every page
            if settings.PAGE_AUTOMATIC_SLUG_RENAMING:
                def is_slug_safe(slug):
                    content = Content.objects.get_content_slug_by_slug(slug)
                    if content is None:
                        return True
                    if self.instance.id:
                        if content.page.id == self.instance.id:
                            return True
                    else:
                        return False

                return automatic_slug_renaming(slug, is_slug_safe)

            if settings.PAGE_UNIQUE_SLUG_REQUIRED:
                # We can return here as not futher checks
                # are necessary
                return unique_slug_required(self, slug)

            intersects_sites = intersect_sites_method(self)

            if not settings.PAGE_UNIQUE_SLUG_REQUIRED:
                if target and position:
                    target = Page.objects.get(pk=target)
                    if position in ['right', 'left']:
                        slugs = [sibling.slug() for sibling in
                                target.get_siblings()
                                if intersects_sites(sibling)]
                        slugs.append(target.slug())
                        if slug in slugs:
                            raise forms.ValidationError(error_dict['sibling_position_error'])
                    if position == 'first-child':
                        if slug in [sibling.slug() for sibling in
                                    target.get_children()
                                    if intersects_sites(sibling)]:
                            raise forms.ValidationError(error_dict['child_error'])
                else:
                    if self.instance.id:
                        if (slug in [sibling.slug() for sibling in
                            self.instance.get_siblings().exclude(
                                id=self.instance.id
                            ) if intersects_sites(sibling)]):
                            raise forms.ValidationError(error_dict['sibling_error'])
                    else:
                        if slug in [sibling.slug() for sibling in
                                    Page.objects.root()
                                    if intersects_sites(sibling)]:
                            raise forms.ValidationError(error_dict['sibling_root_error'])
            return slug

    return PageForm
