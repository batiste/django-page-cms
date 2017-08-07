from django.db import models
from django.forms import ModelForm
from pages.models import Page
from django.utils.translation import ugettext_lazy as _


class Document(models.Model):
    "A dummy model used to illustrate the use of linked models in django-page-cms"

    title = models.CharField(_('title'), max_length=100, blank=False)
    text = models.TextField(_('text'), blank=True)

    # the foreign key _must_ be called page
    page = models.ForeignKey(Page)


class DocumentForm(ModelForm):
    class Meta:
        model = Document
        fields = "__all__"
