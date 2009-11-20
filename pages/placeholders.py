from django import template
from django.template import Template, TemplateSyntaxError
from django.core.files.storage import FileSystemStorage
from django.forms import Widget, Textarea, ImageField, CharField
from django.conf import settings as global_settings
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import SafeUnicode, mark_safe

from pages import settings
from pages.models import Content, Page
from inspect import isclass, getmembers
import os
import time

def parse_placeholder(parser, token):
    """Parser that understand all the placeholder's parameters."""
    bits = token.split_contents()
    count = len(bits)
    error_string = '%r tag requires at least one argument' % bits[0]
    if count <= 1:
        raise template.TemplateSyntaxError(error_string)
    name = bits[1]
    remaining = bits[2:]
    params = {}
    while remaining:
        bit = remaining[0]
        if bit not in ('as', 'on', 'with', 'parsed'):
            raise template.TemplateSyntaxError(
                "%r is not an correct option for a placeholder" % bit)
        if bit in ('as', 'on', 'with'):
            if len(remaining) < 2:
                raise template.TemplateSyntaxError(
                "Placeholder option '%s' need a parameter" % bit)
            if bit == 'as':
                params['as_varname'] = remaining[1]
            if bit == 'with':
                params['widget'] = remaining[1]
            if bit == 'on':
                params['page'] = remaining[1]
            remaining = remaining[2:]
        else:
            params['parsed'] = True
            remaining = remaining[1:]
    return name, params


class PlaceholderNode(template.Node):
    """This template node is used to output page content and
    dynamically generate input fields in the admin.

    :param name: the name of the placeholder you want to show/create
    :param page: the optional page object
    :param widget: the widget you want to use in the admin interface. Take
        a look into :mod:`pages.admin.widgets` to see which widgets
        are available.
    :param parsed: if the ``parsed`` word is given, the content of the
        placeholder is evaluated as template code, within the current context.
    :param as_varname: if ``as_varname`` is defined, no value will be returned.
        A variable will be created in the context with the defined name.
    """

    field = CharField

    def __init__(self, name, page=None, widget=None, parsed=False, as_varname=None):
        self.page = page or 'current_page'
        self.name = name
        self.widget = widget
        self.parsed = parsed
        self.as_varname = as_varname
        self.found_in_block = None

    def get_widget(self, page, language, fallback=Textarea):
        """Given the name of a placeholder return a ``Widget`` subclass
        like Textarea or TextInput."""
        from pages.admin import widgets
        name = self.widget
        if name and '.' in name:
            name = str(name)
            module_name, class_name = name.rsplit('.', 1)
            module = __import__(module_name, {}, {}, [class_name])
            widget_class = getattr(module, class_name, fallback)
        else:
            widget_class = dict(getmembers(widgets, isclass)).get(name, fallback)
        if not isinstance(widget_class(), Widget):
            widget_class = fallback
        try:
            widget = widget_class(language=language, page=page)
        except TypeError:
            widget = widget_class()
        return widget

    def get_field(self, page, language, initial=None):
        """The field that will be shown within the admin."""
        if self.parsed:
            help_text = _('Note: This field is evaluated as template code.')
        else:
            help_text = ""
        widget = self.get_widget(page, language)
        return self.field(widget=widget, initial=initial,
                    help_text=help_text, required=False)

    def save(self, page, language, data, change):
        """Actually save the placeholder data into the Content object."""
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

    def render(self, context):
        """Output the content of the node in the template."""
        if not self.page in context:
            return ''
        # current_page can be set to None
        if not context[self.page]:
            return ''

        lang = context.get('lang', settings.PAGE_DEFAULT_LANGUAGE)
        content = Content.objects.get_content(context[self.page], lang,
                                              self.name, True)
        if not content:
            return ''
        if self.parsed:
            try:
                t = template.Template(content, name=self.name)
                content = mark_safe(t.render(context))
            except template.TemplateSyntaxError, error:
                if global_settings.DEBUG:
                    error = PLACEHOLDER_ERROR % {
                        'name': self.name,
                        'error': error,
                    }
                    if self.as_varname is None:
                        return error
                    context[self.as_varname] = error
                    return ''
                else:
                    return ''
        if self.as_varname is None:
            return content
        context[self.as_varname] = content
        return ''

    def __repr__(self):
        return "<Placeholder Node: %s>" % self.name


class ImagePlaceholderNode(PlaceholderNode):

    def __init__(self, name, *args, **kwargs):
        super(ImagePlaceholderNode, self).__init__(name, *args, **kwargs)

    def get_field(self, page, language, initial=None):
        help_text = ""
        widget = self.get_widget(page, language)
        return ImageField(
            widget=widget,
            initial=initial,
            help_text=help_text,
            required=False
        )

    def save(self, page, language, data, change):
        filename = ""
        if page and page.id and data:
            storage = FileSystemStorage()
            filename = os.path.join('upload', 'page_'+str(page.id),
                self.name + '-' + str(time.time()))
            filename = storage.save(filename, data)
            super(ImagePlaceholderNode, self).save(
                page,
                language,
                filename,
                change
            )
