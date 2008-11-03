from django import forms
from django.conf import settings
from django.utils.safestring import mark_safe

class RichTextarea(forms.Textarea):
    def __init__(self, attrs=None):
        attrs = {'class': 'rte'}
        super(RichTextarea, self).__init__(attrs)

class WYMEditor(forms.Textarea):
    class Media:
        js = (
            'javascript/jquery.js',
            'wymeditor/jquery.wymeditor.js',
            'wymeditor/plugins/resizable/jquery.wymeditor.resizable.js',
        )

    def __init__(self, language=None, attrs=None):
        self.language = language or settings.LANGUAGE_CODE[:2]
        self.attrs = {'class': 'wymeditor'}
        if attrs:
            self.attrs.update(attrs)
        super(WYMEditor, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        rendered = super(WYMEditor, self).render(name, value, attrs)
        return rendered + mark_safe(u'''<script type="text/javascript">
            jQuery('#id_%s').wymeditor({
                lang: '%s',
                skin:'django',
                updateSelector: '.submit-row input[type=submit],',
                updateEvent: 'click',
                postInit: function(wym) {
                    wym.resizable({handles: "s", maxHeight: 600});
                }
            });
            </script>''' % (name, self.language))
