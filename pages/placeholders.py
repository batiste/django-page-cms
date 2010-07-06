"""Placeholder module, that's where the smart things appened."""

from pages.widgets_registry import get_widget
from pages import settings
from pages.models import Content
from pages.widgets import ImageInput, VideoWidget

from django import template
from django.template import TemplateSyntaxError
from django.core.files.storage import FileSystemStorage
from django.forms import Textarea, ImageField, CharField
from django.forms import TextInput
from django.conf import settings as global_settings
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string

import os
import time
import re

PLACEHOLDER_ERROR = _("[Placeholder %(name)s had syntax error: %(error)s]")

def parse_placeholder(parser, token):
    """Parse the `PlaceholderNode` parameters.

    Return a tuple with the name and parameters."""
    bits = token.split_contents()
    count = len(bits)
    error_string = '%r tag requires at least one argument' % bits[0]
    if count <= 1:
        raise TemplateSyntaxError(error_string)
    name = bits[1]
    remaining = bits[2:]
    params = {}
    simple_options = ['parsed', 'inherited', 'untranslated']
    param_options = ['as', 'on', 'with']
    all_options = simple_options + param_options
    while remaining:
        bit = remaining[0]
        if bit not in all_options:
            raise TemplateSyntaxError(
                "%r is not an correct option for a placeholder" % bit)
        if bit in param_options:
            if len(remaining) < 2:
                raise TemplateSyntaxError(
                "Placeholder option '%s' need a parameter" % bit)
            if bit == 'as':
                params['as_varname'] = remaining[1]
            if bit == 'with':
                params['widget'] = remaining[1]
            if bit == 'on':
                params['page'] = remaining[1]
            remaining = remaining[2:]
        elif bit == 'parsed':
            params['parsed'] = True
            remaining = remaining[1:]
        elif bit == 'inherited':
            params['inherited'] = True
            remaining = remaining[1:]
        elif bit == 'untranslated':
            params['untranslated'] = True
            remaining = remaining[1:]
    return name, params


class PlaceholderNode(template.Node):
    """This template node is used to output page content and
    dynamically generate input fields in the admin.

    :param name: the name of the placeholder you want to show/create
    :param page: the optional page object
    :param widget: the widget you want to use in the admin interface. Take
        a look into :mod:`pages.widgets` to see which widgets
        are available.
    :param parsed: if the ``parsed`` word is given, the content of the
        placeholder is evaluated as template code, within the current
        context.
    :param as_varname: if ``as_varname`` is defined, no value will be
        returned. A variable will be created in the context
        with the defined name.
    :param inherited: inherit content from parent's pages.
    :param untranslated: the placeholder's content is the same for
        every language.
    """

    field = CharField
    widget = TextInput

    def __init__(self, name, page=None, widget=None, parsed=False,
            as_varname=None, inherited=False, untranslated=False):
        """Gather parameters for the `PlaceholderNode`.

        These values should be thread safe and don't change between calls."""
        self.page = page or 'current_page'
        self.name = name
        if widget:
            self.widget = widget
        self.parsed = parsed
        self.inherited = inherited
        self.untranslated = untranslated
        self.as_varname = as_varname
        self.found_in_block = None

    def get_widget(self, page, language, fallback=Textarea):
        """Given the name of a placeholder return a `Widget` subclass
        like Textarea or TextInput."""
        is_str = type(self.widget) == type(str())
        is_unicode = type(self.widget) == type(unicode())
        if is_str or is_unicode:
            widget = get_widget(self.widget)
        else:
            widget = self.widget
        try:
            return widget(page=page, language=language)
        except:
            pass
        return widget()

    def get_extra_data(self, data):
        """Get eventual extra data for this placeholder from the
        POST dictionary."""
        result = {}
        for key in data.keys():
            if key.startswith(self.name+'-'):
                new_key = key.replace(self.name+'-', '')
                result[new_key] = data[key]
        return result

    def get_field(self, page, language, initial=None):
        """The field that will be shown within the admin."""
        if self.parsed:
            help_text = _('Note: This field is evaluated as template code.')
        else:
            help_text = ''
        widget = self.get_widget(page, language)
        return self.field(widget=widget, initial=initial,
                    help_text=help_text, required=False)

    def save(self, page, language, data, change, extra_data=None):
        """Actually save the placeholder data into the Content object."""
        # if this placeholder is untranslated, we save everything
        # in the default language
        if self.untranslated:
            language = settings.PAGE_DEFAULT_LANGUAGE
        
        # the page is being changed
        if change:
            # we need create a new content if revision is enabled
            if(settings.PAGE_CONTENT_REVISION and self.name
                not in settings.PAGE_CONTENT_REVISION_EXCLUDE_LIST):
                Content.objects.create_content_if_changed(
                    page,
                    language,
                    self.name,
                    data
                )
            else:
                Content.objects.set_or_create_content(
                    page,
                    language,
                    self.name,
                    data
                )
        # the page is being added
        else:
            Content.objects.set_or_create_content(
                page,
                language,
                self.name,
                data
            )

    def get_content(self, page_obj, lang, lang_fallback=True):
        if self.untranslated:
            lang = settings.PAGE_DEFAULT_LANGUAGE
            lang_fallback = False
        content = Content.objects.get_content(page_obj, lang, self.name,
            lang_fallback)
        if self.inherited and not content:
            for ancestor in page_obj.get_ancestors():
                content = Content.objects.get_content(ancestor, lang,
                    self.name, lang_fallback)
                if content:
                    break
        return content

    def get_content_from_context(self, context):
        if not self.page in context:
            return ''
        # current_page can be set to None
        if not context[self.page]:
            return ''

        if self.untranslated:
            lang_fallback = False
            lang = settings.PAGE_DEFAULT_LANGUAGE
        else:
            lang_fallback = True
            lang = context.get('lang', settings.PAGE_DEFAULT_LANGUAGE)
        return self.get_content(context[self.page], lang, lang_fallback)

    def render(self, context):
        """Output the content of the `PlaceholdeNode` in the template."""

        content = self.get_content_from_context(context)
        if not content:
            return ''
        if self.parsed:
            try:
                t = template.Template(content, name=self.name)
                content = mark_safe(t.render(context))
            except TemplateSyntaxError, error:
                if global_settings.DEBUG:
                    content = PLACEHOLDER_ERROR % {
                        'name': self.name,
                        'error': error,
                    }
                else:
                    content = ''
        if self.as_varname is None:
            return content
        context[self.as_varname] = content
        return ''

    def __repr__(self):
        return "<Placeholder Node: %s>" % self.name


class ImagePlaceholderNode(PlaceholderNode):
    """A `PlaceholderNode` that saves one image on disk.

    `PAGE_UPLOAD_ROOT` setting define where to save the image.
    """

    def get_field(self, page, language, initial=None):
        help_text = ""
        widget = ImageInput(page, language)
        return ImageField(
            widget=widget,
            initial=initial,
            help_text=help_text,
            required=False
        )

    def save(self, page, language, data, change, extra_data=None):
        if 'delete' in extra_data:
            return super(ImagePlaceholderNode, self).save(
                page,
                language,
                "",
                change
            )
        filename = ''
        if change and data:
            # the image URL is posted if not changed
            if type(data) is unicode:
                return
            storage = FileSystemStorage()
            filename = os.path.join(
                settings.PAGE_UPLOAD_ROOT,
                'page_'+str(page.id),
                self.name + '-' + str(time.time())
            )

            m = re.search('\.[a-zA-Z]{1,4}$', str(data))
            if m is not None:
                filename += m.group(0).lower()

            filename = storage.save(filename, data)
            return super(ImagePlaceholderNode, self).save(
                page,
                language,
                filename,
                change
            )

class VideoPlaceholderNode(PlaceholderNode):
    """A youtube `PlaceholderNode`, just here as an example."""

    widget = VideoWidget

    def render(self, context):
        content = self.get_content_from_context(context)
        if not content:
            return ''
        if content:
            video_url, w, h = content.split('\\')
            m = re.search('youtube\.com\/watch\?v=([^&]+)', content)
            if m:
                video_url = 'http://www.youtube.com/v/'+m.group(1)
            if not w:
                w = 425
            if not h:
                h = 344
            context = {'video_url': video_url, 'w':w, 'h':h}
            renderer = render_to_string('pages/embed.html', context)
            return mark_safe(renderer)
        return ''
