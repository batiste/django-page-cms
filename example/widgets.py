from django.forms import Textarea
from django.utils.safestring import mark_safe
from pages.settings import PAGES_MEDIA_URL

class CustomTextarea(Textarea):
    """class Media:
        js = ['path to your javascript']
        css = {
            'all': ['path to your CSS']
        }"""

    def __init__(self, attrs=None):
        attrs = {'class': 'custom-textarea'}
        super(CustomTextarea, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        rendered = super(CustomTextarea, self).render(name, value, attrs)
        return mark_safe("""Take a look at \
                example.widgets.CustomTextarea<br>""") \
                + rendered