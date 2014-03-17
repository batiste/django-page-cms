# -*- coding: utf-8 -*-
"""Django CMS come with a set of ready to use widgets that you can enable
in the admin via a placeholder tag in your template."""

from pages.settings import PAGES_MEDIA_URL, PAGE_TAGGING
from pages.settings import PAGE_LANGUAGES
from pages.models import Page
from pages.widgets_registry import register_widget

from django.conf import settings
from django import forms
from django.forms import TextInput, Textarea, HiddenInput
from django.forms import MultiWidget, FileInput
from django.forms.util import flatatt
from django.contrib.admin.widgets import AdminTextInputWidget
from django.contrib.admin.widgets import AdminTextareaWidget
from django.utils.safestring import mark_safe
from django.utils.html import format_html
from django.utils.encoding import force_text
from django.template.loader import render_to_string
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext as _

from os.path import join

register_widget(TextInput)
register_widget(Textarea)
register_widget(AdminTextInputWidget)
register_widget(AdminTextareaWidget)


class RichTextarea(Textarea):
    """A RichTextarea widget."""
    class Media:
        js = [join(PAGES_MEDIA_URL, path) for path in (
            'javascript/jquery.js',
        )]
        css = {
            'all': [join(PAGES_MEDIA_URL, path) for path in (
                'css/rte.css',
            )]
        }

    def __init__(self, language=None, attrs=None, **kwargs):
        attrs = {'class': 'rte'}
        self.language = language
        super(RichTextarea, self).__init__(attrs)

    def render(self, name, value, attrs=None, **kwargs):
        rendered = super(RichTextarea, self).render(name, value, attrs)
        context = {
            'name': name,
            'PAGES_MEDIA_URL': PAGES_MEDIA_URL,
        }
        return rendered + mark_safe(render_to_string(
            'pages/widgets/richtextarea.html', context))
register_widget(RichTextarea)


class CKEditor(Textarea):
     """CKEditor widget."""

     class Media:
         js = [join(PAGES_MEDIA_URL, 'ckeditor/ckeditor.js'),
             join(settings.MEDIA_URL, 'filebrowser/js/FB_CKEditor.js'),
         ]

     def __init__(self, language=None, attrs=None, **kwargs):
         self.language = language
         self.filebrowser = "filebrowser" in getattr(settings,
             'INSTALLED_APPS', [])
         self.attrs = {'class': 'ckeditor'}
         if attrs:
             self.attrs.update(attrs)
         super(CKEditor, self).__init__(attrs)

     def render(self, name, value, attrs=None, **kwargs):
         rendered = super(CKEditor, self).render(name, value, attrs)
         context = {
             'name': name,
             'filebrowser': self.filebrowser,
         }
         return rendered + mark_safe(render_to_string(
             'pages/widgets/ckeditor.html', context))

register_widget(CKEditor)


class ImageInput(FileInput):

    def __init__(self, page=None, language=None, attrs=None, **kwargs):
        self.language = language
        self.page = page
        super(ImageInput, self).__init__(attrs)

    def render(self, name, value, attrs=None, **kwargs):
        if not self.page:
            field_content = _('Please save the page to show the image field')
        else:
            field_content = ''
            if value:
                field_content += _('Current file: %s<br/>') % value
            field_content += super(ImageInput, self).render(name, attrs)
            if value:
                field_content += '''<br><label for="%s-delete">%s</label>
                    <input name="%s-delete" id="%s-delete"
                    type="checkbox" value="true">
                    ''' % (name, _('Delete image'), name, name)
        return mark_safe(field_content)
register_widget(ImageInput)


class FileInput(FileInput):

    def __init__(self, page=None, language=None, attrs=None, **kwargs):
        self.language = language
        self.page = page
        super(FileInput, self).__init__(attrs)

    def render(self, name, value, attrs=None, **kwargs):
        if not self.page:
            field_content = _('Please save the page to show the file field')
        else:
            field_content = ''
            if value:
                field_content += _('Current file: %s<br/>') % value
            field_content += super(FileInput, self).render(name, attrs)
            if value:
                field_content += '''<br><label for="%s-delete">%s</label>
                    <input name="%s-delete" id="%s-delete"
                    type="checkbox" value="true">
                    ''' % (name, _('Delete file'), name, name)
        return mark_safe(field_content)
register_widget(FileInput)


class LanguageChoiceWidget(TextInput):

    def __init__(self, language=None, attrs=None, **kwargs):
        self.language = language
        self.page = kwargs.get('page')
        # page is None
        super(LanguageChoiceWidget, self).__init__(attrs)

    def render(self, name, value, attrs=None, **kwargs):
        context = {
            'name': name,
            'value': value,
            'page': self.page,
            'language': value,
            'page_languages': PAGE_LANGUAGES
        }
        return mark_safe(render_to_string(
            'pages/widgets/languages.html', context))


class PageLinkWidget(MultiWidget):
    '''A page link `Widget` for the admin.'''
    def __init__(self, attrs=None, page=None, language=None,
        video_url=None, linkedpage=None, text=None):
            l = [('', '----')]
            for p in Page.objects.all():
                l.append((p.id, str(p)))
            widgets = [
                forms.Select(choices=l),
                TextInput(attrs=attrs)
            ]
            super(PageLinkWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        import json
        try:
            return json.loads(value)
        except:
            pass
        return []

    def value_from_datadict(self, data, files, name):
        import json
        value = ['', '']
        for da in [x for x in data if x.startswith(name)]:
            index = int(da[len(name) + 1:])
            value[index] = data[da]
        if value[0] == value[1] == '':
            return None
        return json.dumps(value)

    def _has_changed(self, initial, data):
        """Need to be reimplemented to be correct."""
        if data == initial:
            return False
        return bool(initial) != bool(data)

    def format_output(self, rendered_widgets):
        """
        Given a list of rendered widgets (as strings), it inserts an HTML
        linebreak between them.

        Returns a Unicode string representing the HTML for the whole lot.
        """
        return """<table>
            <tr><td>page</td><td>%s</td></tr>
            <tr><td>text</td><td>%s</td></tr>
        </table>""" % tuple(rendered_widgets)
register_widget(PageLinkWidget)


