# -*- coding: utf-8 -*-
"""Django CMS come with a set of ready to use widgets that you can enable
in the admin via a placeholder tag in your template."""

from pages.settings import PAGES_MEDIA_URL, PAGE_TAGGING
from pages.settings import PAGE_TINYMCE, PAGE_LANGUAGES
from pages.models import Page
from pages.widgets_registry import register_widget

from django.conf import settings
from django.forms import TextInput, Textarea, HiddenInput
from django.forms import MultiWidget, FileInput
from django.contrib.admin.widgets import AdminTextInputWidget
from django.contrib.admin.widgets import AdminTextareaWidget
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext as _

from os.path import join

register_widget(TextInput)
register_widget(Textarea)
register_widget(AdminTextInputWidget)
register_widget(AdminTextareaWidget)

if "filebrowser" in getattr(settings, 'INSTALLED_APPS', []):
    from filebrowser.fields import FileBrowseWidget
    class FileBrowseInput(FileBrowseWidget):
        """FileBrowseInput widget."""

        def __init__(self, attrs={}):
            super(FileBrowseInput, self).__init__(attrs)
    register_widget(FileBrowseInput)


if PAGE_TAGGING:
    from tagging.models import Tag
    from django.utils import simplejson

    class AutoCompleteTagInput(TextInput):
        """An autocompete widget"""
        class Media:
            js = [join(PAGES_MEDIA_URL, path) for path in (
                'javascript/jquery.js',
                'javascript/jquery.bgiframe.min.js',
                'javascript/jquery.ajaxQueue.js',
                'javascript/jquery.autocomplete.min.js'
            )]

        def __init__(self, language=None, attrs=None, **kwargs):
            self.language = language
            super(AutoCompleteTagInput, self).__init__(attrs)

        def render(self, name, value, language=None, attrs=None, **kwargs):
            rendered = super(AutoCompleteTagInput, self).render(
                name, value, attrs)
            page_tags = Tag.objects.usage_for_model(Page)
            context = {
                'name': name,
                'tags': simplejson.dumps([tag.name for tag in page_tags],
                    ensure_ascii=False),
            }
            return rendered + mark_safe(render_to_string(
            'pages/widgets/autocompletetaginput.html', context))

    register_widget(AutoCompleteTagInput)

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

if PAGE_TINYMCE:
    from tinymce import widgets as tinymce_widgets

    class TinyMCE(tinymce_widgets.TinyMCE):
        """TinyMCE widget."""
        def __init__(self, language=None, attrs=None, mce_attrs=None,
                                                                **kwargs):
            self.language = language

            if mce_attrs is None:
                mce_attrs = {}

            self.mce_attrs = mce_attrs
            self.mce_attrs.update({
                'mode': "exact",
                'theme': "advanced",
                'width': 640,
                'height': 400,
                'theme_advanced_toolbar_location': "top",
                'theme_advanced_toolbar_align': "left"
            })
            # take into account the default settings, don't allow
            # the above hard coded ones overriding them
            self.mce_attrs.update(
                getattr(settings, 'TINYMCE_DEFAULT_CONFIG', {}))
            super(TinyMCE, self).__init__(language, attrs, mce_attrs)
    register_widget(TinyMCE)

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

class WYMEditor(Textarea):
    """WYMEditor widget."""

    class Media:
        js = [join(PAGES_MEDIA_URL, path) for path in (
            'javascript/jquery.js',
            'javascript/jquery.ui.js',
            'javascript/jquery.ui.resizable.js',
            'wymeditor/jquery.wymeditor.js',
            'wymeditor/plugins/resizable/jquery.wymeditor.resizable.js',
        )]

        if "filebrowser" in getattr(settings, 'INSTALLED_APPS', []):
            js.append(join(PAGES_MEDIA_URL,
            'wymeditor/plugins/filebrowser/jquery.wymeditor.filebrowser.js'))

    def __init__(self, language=None, attrs=None, **kwargs):
        self.language = language or getattr(settings, 'LANGUAGE_CODE')
        self.attrs = {'class': 'wymeditor'}
        if attrs:
            self.attrs.update(attrs)
        super(WYMEditor, self).__init__(attrs)

    def render(self, name, value, attrs=None, **kwargs):
        rendered = super(WYMEditor, self).render(name, value, attrs)
        context = {
            'name': name,
            'lang': self.language[:2],
            'language': self.language,
            'PAGES_MEDIA_URL': PAGES_MEDIA_URL,
        }
        context['page_link_wymeditor'] = 1
        context['page_list'] = Page.objects.all().order_by('tree_id','lft')

        context['filebrowser'] = 0
        if "filebrowser" in getattr(settings, 'INSTALLED_APPS', []):
            context['filebrowser'] = 1

        return rendered + mark_safe(render_to_string(
            'pages/widgets/wymeditor.html', context))

register_widget(WYMEditor)

class markItUpMarkdown(Textarea):
    """markItUpMarkdown widget."""

    class Media:
        js = [join(PAGES_MEDIA_URL, path) for path in (
            'javascript/jquery.js',
            'markitup/jquery.markitup.js',
            'markitup/sets/markdown/set.js',
        )]
        css = {
            'all': [join(PAGES_MEDIA_URL, path) for path in (
                'markitup/skins/simple/style.css',
                'markitup/sets/markdown/style.css',
            )]
        }

    def render(self, name, value, attrs=None, **kwargs):
        rendered = super(markItUpMarkdown, self).render(name, value, attrs)
        context = {
            'name': name,
        }
        return rendered + mark_safe(render_to_string(
            'pages/widgets/markitupmarkdown.html', context))
register_widget(markItUpMarkdown)

class markItUpHTML(Textarea):
    """markItUpHTML widget."""

    class Media:
        js = [join(PAGES_MEDIA_URL, path) for path in (
            'javascript/jquery.js',
            'markitup/jquery.markitup.js',
            'markitup/sets/default/set.js',
        )]
        css = {
            'all': [join(PAGES_MEDIA_URL, path) for path in (
                'markitup/skins/simple/style.css',
                'markitup/sets/default/style.css',
            )]
        }

    def render(self, name, value, attrs=None, **kwargs):
        rendered = super(markItUpHTML, self).render(name, value, attrs)
        context = {
            'name': name,
        }
        return rendered + mark_safe(render_to_string(
            'pages/widgets/markituphtml.html', context))
register_widget(markItUpHTML)


class EditArea(Textarea):
    """EditArea is a html syntax coloured widget."""
    class Media:
        js = [join(PAGES_MEDIA_URL, path) for path in (
            'edit_area/edit_area_full.js',
        )]

    def __init__(self, language=None, attrs=None, **kwargs):
        self.language = language
        self.attrs = {'class': 'editarea'}
        if attrs:
            self.attrs.update(attrs)
        super(EditArea, self).__init__(attrs)

    def render(self, name, value, attrs=None, **kwargs):
        rendered = super(EditArea, self).render(name, value, attrs)
        context = {
            'name': name,
            'language': self.language,
            'PAGES_MEDIA_URL': PAGES_MEDIA_URL,
        }
        return rendered + mark_safe(render_to_string(
            'pages/widgets/editarea.html', context))
register_widget(EditArea)

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


class VideoWidget(MultiWidget):
    '''A youtube `Widget` for the admin.'''
    def __init__(self, attrs=None, page=None, language=None,
        video_url=None, weight=None, height=None):
            widgets = [
                TextInput(attrs=attrs),
                TextInput(attrs=attrs),
                TextInput(attrs=attrs)
            ]
            super(VideoWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        # backslashes are forbidden in URLs
        if value:
            return value.split('\\')
        return (None, None, None)

    def value_from_datadict(self, data, files, name):
        value = [u'', u'', u'']
        for da in filter(lambda x: x.startswith(name), data):
            index = int(da[len(name)+1:])
            value[index] = data[da]
        if value[0] == value[1] == value[2] == u'':
            return None
        return u'%s\\%s\\%s' % tuple(value)

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
        return u"""<table>
            <tr><td>url</td><td>%s</td></tr>
            <tr><td>width</td><td>%s</td></tr>
            <tr><td>weight</td><td>%s</td></tr>
        </table>""" % tuple(rendered_widgets)


register_widget(VideoWidget)


class LanguageChoiceWidget(TextInput):

    def __init__(self, language=None, attrs=None, **kwargs):
        self.language = language
        self.page = kwargs.get('page')
        # page is None
        super(LanguageChoiceWidget, self).__init__(attrs)

    def render(self, name, value, attrs=None, **kwargs):
        context = {
            'name': name,
            'value':value,
            'page':self.page,
            'language': value,
            'page_languages':PAGE_LANGUAGES
        }
        return mark_safe(render_to_string(
            'pages/widgets/languages.html', context))
