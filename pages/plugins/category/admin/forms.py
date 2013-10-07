from ..models import Category

class CategoryForm(SlugFormMixin):
    """Form for category creation"""

    err_dict = {
        'another_category_error': _('Another category with this slug already exists'),
    }

    language = forms.ChoiceField(
        label=_('Language'),
        choices=settings.PAGE_LANGUAGES,
        widget=LanguageChoiceWidget()
    )

    class Meta:
        model = Category

    def clean_slug(self):
        """Slug cleanup"""

        slug = slugify(self.cleaned_data['slug'])

        if settings.PAGE_AUTOMATIC_SLUG_RENAMING:
            def is_slug_safe(slug):
                try:
                    category = Category.objects.get(slug=slug)
                except Category.DoesNotExist:
                    category = None
                if category is None:
                    return True
                if self.instance.id:
                    if category.id == self.instance.id:
                        return True
                else:
                    return False

            return self._clean_page_automatic_slug_renaming(slug, is_slug_safe)

        if settings.PAGE_UNIQUE_SLUG_REQUIRED:
            if Category.objects.filter(slug=slug).exists():
                raise forms.ValidationError(self.err_dict['another_category_error'])

        return slug



