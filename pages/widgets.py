# -*- coding: utf-8 -*-
"""Django CMS come with a set of ready to use widgets that you can enable
in the admin via a placeholder tag in your template."""

from pages.settings import PAGES_MEDIA_URL, PAGES_STATIC_URL
from pages.settings import PAGE_LANGUAGES
from pages.models import Page
from pages.widgets_registry import register_widget

from django import forms
from django.forms import TextInput, Textarea
from django.forms import MultiWidget
from django.forms import FileInput as DFileInput
from django.contrib.admin.widgets import AdminTextInputWidget
from django.contrib.admin.widgets import AdminTextareaWidget
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

from os.path import join

register_widget(TextInput)
register_widget(Textarea)
register_widget(AdminTextInputWidget)
register_widget(AdminTextareaWidget)


class RichTextarea(Textarea):
    """A RichTextarea widget."""
    class Media:
        js = [join(PAGES_STATIC_URL, path) for path in (
            'javascript/jquery.js',
            'javascript/jquery.rte.js'
        )]
        css = {
            'all': [join(PAGES_STATIC_URL, path) for path in (
                'css/rte.css',
                'css/font-awesome.min.css'
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
            'PAGES_STATIC_URL': PAGES_STATIC_URL,
            'PAGES_MEDIA_URL': PAGES_MEDIA_URL,
        }
        return rendered + mark_safe(render_to_string(
            'pages/widgets/richtextarea.html', context))


register_widget(RichTextarea)


insert_image_link = '''
<br>
<button title='insert image from the media library' class='image-lookup-{name}'>
    From media library
</button>
<input name="{name}-selected" id="{name}-selected" type="hidden">
<span id="{name}-selected-value">
</span>

<br><label for="{name}-delete">
<input name="{name}-delete" style="display:inline-block" id="{name}-delete" type="checkbox" value="true"> {del_msg}
</label>
<br style="clear:both">


<script>
$(function(){{
    function dismissRelatedLookupPopup(win, chosenId) {{
        $.get('/admin/pages/page/' + chosenId + '/media-url/', function(response) {{
            console.log(response);
            $('#{name}-selected').val(response);
            $('#{name}-selected-value').text(response);
        }});
        win.close();
        window.dismissRelatedLookupPopup = oldDismissRelatedLookupPopup;
        window.dismissAddRelatedObjectPopup = oldDismissAddRelatedObjectPopup;
    }}
    function showMediaAdminPopup() {{
        var name = 'mediaWindowSelect';
        var href = '/admin/pages/media/?_to_field=id&_popup=1';
        window.dismissRelatedLookupPopup = dismissRelatedLookupPopup;
        window.dismissAddRelatedObjectPopup = dismissRelatedLookupPopup;
        var win = window.open(href, name, 'height=500,width=800,resizable=yes,scrollbars=yes');
        win.focus();
        return false;
    }}
    $('.image-lookup-{name}').click(function(e) {{
        e.preventDefault();
        showMediaAdminPopup();
        return false;
    }});
}});

</script>
'''

class FileInput(DFileInput):

    def __init__(self, page=None, language=None, attrs=None, **kwargs):
        self.language = language
        self.page = page
        super(FileInput, self).__init__(attrs)

    please_save_msg = _('Please save the page to show the file field')
    delete_msg = _('Delete file')

    def render(self, name, value, attrs=None, **kwargs):
        if not self.page:
            field_content = self.please_save_msg
        else:
            field_content = '<span class="placeholder-fileinput">'
            if value:
                field_content += _('Current file: %s<br/>') % value
                field_content += '<hr>'
            field_content += super(FileInput, self).render(name, attrs)
            field_content += insert_image_link.format(
                name=name,
                del_msg=self.delete_msg,
                value=value)
            field_content += '</span>'
        return mark_safe(field_content)
register_widget(FileInput)


class ImageInput(FileInput):

    please_save_msg = _('Please save the page to show the image field')
    delete_msg = _('Delete image')

register_widget(ImageInput)


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

    def __init__(
            self, attrs=None, page=None, language=None,
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
