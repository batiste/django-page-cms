from os.path import join
from django.conf import settings
from django.forms import TextInput, Textarea
from django.utils.safestring import mark_safe

from pages.settings import PAGES_MEDIA_URL
from pages.models import Page, tagging

if tagging:

    from tagging.models import Tag
    from django.utils import simplejson

    class AutoCompleteTagInput(TextInput):
        class Media:
            js = [join(PAGES_MEDIA_URL, path) for path in (
                'javascript/jquery.js',
                'javascript/jquery.bgiframe.min.js',
                'javascript/jquery.ajaxQueue.js',
                'javascript/jquery.autocomplete.min.js'
            )]

        def render(self, name, value, attrs=None):
            rendered = super(AutoCompleteTagInput, self).render(name, value, attrs)
            page_tags = Tag.objects.usage_for_model(Page)
            tag_list = simplejson.dumps([tag.name for tag in page_tags],
                                        ensure_ascii=False)
            return rendered + mark_safe(u'''<script type="text/javascript">
                jQuery("#id_%s").autocomplete(%s, {
                    width: 150,
                    max: 10,
                    highlight: false,
                    multiple: true,
                    multipleSeparator: ", ",
                    scroll: true,
                    scrollHeight: 300,
                    matchContains: true,
                    autoFill: true,
                });
                </script>''' % (name, tag_list))


class RichTextarea(Textarea):
    def __init__(self, attrs=None):
        attrs = {'class': 'rte'}
        super(RichTextarea, self).__init__(attrs)

class WYMEditor(Textarea):
    class Media:
        js = [join(PAGES_MEDIA_URL, path) for path in (
            'javascript/jquery.js',
            'wymeditor/jquery.wymeditor.js',
            'wymeditor/plugins/resizable/jquery.wymeditor.resizable.js',
        )]

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

class markItUpMarkdown(Textarea):
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

    def render(self, name, value, attrs=None):
        rendered = super(markItUpMarkdown, self).render(name, value, attrs)
        return rendered + mark_safe(u'''<script type="text/javascript">
        $('#id_%s').markItUp(mySettings);</script>''' % name)

class markItUpHTML(Textarea):
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

    def render(self, name, value, attrs=None):
        rendered = super(markItUpHTML, self).render(name, value, attrs)
        return rendered + mark_safe(u'''<script type="text/javascript">
        $('#id_%s').markItUp(mySettings);</script>''' % name)
