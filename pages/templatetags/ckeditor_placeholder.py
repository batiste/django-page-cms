from django import template
from django.forms import Textarea
from django.utils import translation
from django.conf import settings

from pages.placeholders import PlaceholderNode
from pages.placeholders import parse_placeholder

register = template.Library()

class CKEditorPlaceholderNode(PlaceholderNode):
    def get_widget(self, page, language, fallback=Textarea):
        if 'ckeditor' not in settings.INSTALLED_APPS:
            return fallback

        from ckeditor.widgets import CKEditorWidget

        with_stmt = self.widget # name of the widget as called in template like...
        # {% ckeditor_placeholder "welcome" with text_wysiwym_widget:default%}
        splitted = with_stmt.split(":")

        if len(splitted) == 1:
            ck = CKEditorWidget(config_name='default')
        elif len(splitted) > 1:
            ck = CKEditorWidget(config_name=splitted[1])

        if not ck.config.get('language'):
            ck.config['language'] = translation.get_language()

        return ck

def do_ckeditorplaceholder(parser, token):
    name, params = parse_placeholder(parser, token)
    return CKEditorPlaceholderNode(name, **params)

register.tag('ckeditor_placeholder', do_ckeditorplaceholder)
