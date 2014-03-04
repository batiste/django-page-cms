from ..models import Category
from .forms import CategoryForm
from django.contrib import admin
from pages.phttp import get_language_from_request, get_template_from_request
from os.path import join
from pages import settings
from django.contrib.admin.sites import AlreadyRegistered


class CategoryAdmin(admin.ModelAdmin):
    class Media:
        css = {
            'all': [join(settings.PAGES_MEDIA_URL, path) for path in (
                'css/rte.css',
                'css/pages.css'
            )]
        }
        js = [join(settings.PAGES_MEDIA_URL, path) for path in (
            'javascript/jquery.js',
            'javascript/jquery.rte.js',
            'javascript/pages.js',
            'javascript/pages_list.js',
            'javascript/pages_form.js',
            'javascript/jquery.query-2.1.7.js',
        )]

    def get_form(self, request, obj=None, **kwargs):
        """Get a :class:`Category <pages.admin.forms.CategoryForm>` for the
        :class:`Category <pages.models.Category>` and modify its fields depending on
        the request."""
        form = super(CategoryAdmin, self).get_form(request, obj, **kwargs)

        language = get_language_from_request(request)
        form.base_fields['language'].initial = language

        return form

    form = CategoryForm
    mandatory_placeholders = ('title', 'slug')
    list_display = ('title', 'slug', 'language')

try:
    admin.site.register(Category, CategoryAdmin)
except AlreadyRegistered:
    pass


