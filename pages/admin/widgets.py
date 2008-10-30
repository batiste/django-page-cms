from django import forms
from django.conf import settings
from django.utils.safestring import mark_safe

class RichTextarea(forms.Textarea):
    def __init__(self, attrs=None):
        attrs = {'class': 'rte'}
        super(RichTextarea, self).__init__(attrs)

class WYMEditor(forms.Textarea):
    def __init__(self, name, stylesheet=None, skin_path=None, language=None, attrs=None):
        self.options = {
            'media_url': settings.MEDIA_URL+'javascript/',
            'name': name,
            'stylesheet': stylesheet or settings.MEDIA_URL+'css/wymeditor.css',
            'lang': language or settings.LANGUAGE_CODE,
        }
        attrs = {'class': 'wymeditor'}
        super(WYMEditor, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        return super(WYMEditor, self).render(name, value, attrs) + \
            mark_safe(u"""
        <script type="text/javascript"
            src="%(media_url)swymeditor/jquery.wymeditor.pack.js"></script>
        <script type="text/javascript"
            src="%(media_url)swymeditor/plugins/hovertools/jquery.wymeditor.hovertools.js">
        </script>
        <script type="text/javascript"
            src="%(media_url)swymeditor/plugins/resizable/jquery.wymeditor.resizable.js">
        </script>
        <script type="text/javascript">
        jQuery(function() {
            jQuery('.%(name)s').wymeditor({
                stylesheet: '%(stylesheet)s',
                lang: '%(lang)s',
                skin: 'django',
                postInit: function(wym) {
                    wym.hovertools();
                    wym.resizable({handles: "s", maxHeight: 600});
                }
            });
        });
        jQuery(".revisions").show();
        </script>
        """ % self.options)
