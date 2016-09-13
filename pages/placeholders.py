"""Placeholder module, that's where the smart things happen."""
from pages.widgets_registry import get_widget
from pages import settings
from pages.models import Content
from pages.widgets import ImageInput, FileInput
from pages.utils import slugify

from django import forms
from django.core.mail import send_mail
from django import template
from django.template import TemplateSyntaxError
from django.core.files.storage import default_storage
from django.forms import Textarea, ImageField, CharField, FileField
from django.forms import TextInput
from django.conf import settings as global_settings
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from django.utils.text import unescape_string_literal
from django.template.loader import render_to_string
from django.template import RequestContext
from django.core.files.uploadedfile import UploadedFile
import logging
import os
import time
import six

logging.basicConfig()
logger = logging.getLogger("pages")

PLACEHOLDER_ERROR = _("[Placeholder %(name)s had syntax error: %(error)s]")


def parse_placeholder(parser, token):
    """Parse the `PlaceholderNode` parameters.

    Return a tuple with the name and parameters."""
    bits = token.split_contents()
    count = len(bits)
    error_string = '%r tag requires at least one argument' % bits[0]
    if count <= 1:
        raise TemplateSyntaxError(error_string)
    try:
        name = unescape_string_literal(bits[1])
    except ValueError:
        name = bits[1]
    remaining = bits[2:]
    params = {}
    simple_options = ['parsed', 'inherited', 'untranslated']
    param_options = ['as', 'on', 'with', 'section']
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
            if bit == 'section':
                params['section'] = unescape_string_literal(remaining[1])
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
    """This template node is used to output and save page content and
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

    def __init__(
            self, name, page=None, widget=None, parsed=False,
            as_varname=None, inherited=False, untranslated=False,
            has_revision=True, section=None):
        """Gather parameters for the `PlaceholderNode`.

        These values should be thread safe and don't change between calls."""
        self.page = page or 'current_page'
        self.name = name
        self.ctype = name.replace(" ", "_")
        if widget:
            self.widget = widget
        self.parsed = parsed
        self.inherited = inherited
        self.untranslated = untranslated
        self.as_varname = as_varname
        self.section = section

        self.found_in_block = None

    def get_widget(self, page, language, fallback=Textarea):
        """Given the name of a placeholder return a `Widget` subclass
        like Textarea or TextInput."""
        is_str = isinstance(self.widget, six.string_types)
        if is_str:
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
        admin form. This method is called when the Page is
        saved in the admin and passed to the placeholder save
        method."""
        result = {}
        for key in list(data.keys()):
            if key.startswith(self.ctype + '-'):
                new_key = key.replace(self.ctype + '-', '')
                result[new_key] = data[key]
        return result

    def get_field(self, page, language, initial=None):
        """The field that will be shown within the admin."""
        if self.parsed:
            help_text = _('Note: This field is evaluated as template code.')
        else:
            help_text = ''
        widget = self.get_widget(page, language)
        return self.field(
            widget=widget, initial=initial,
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
                    self.ctype,
                    data
                )
            else:
                Content.objects.set_or_create_content(
                    page,
                    language,
                    self.ctype,
                    data
                )
        # the page is being added
        else:
            Content.objects.set_or_create_content(
                page,
                language,
                self.ctype,
                data
            )

    def get_content(self, page_obj, lang, lang_fallback=True):
        if self.untranslated:
            lang = settings.PAGE_DEFAULT_LANGUAGE
            lang_fallback = False
        content = Content.objects.get_content(
            page_obj, lang, self.ctype, lang_fallback)
        if self.inherited and not content:
            for ancestor in page_obj.get_ancestors():
                content = Content.objects.get_content(
                    ancestor, lang,
                    self.ctype, lang_fallback)
                if content:
                    break
        return content

    def get_content_from_context(self, context):
        if self.page not in context:
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

    def get_render_content(self, context):
        return mark_safe(self.get_content_from_context(context))

    def render(self, context):
        """Output the content of the `PlaceholdeNode` as a template."""
        content = self.get_render_content(context)
        if not content:
            return ''
        if self.parsed:
            try:
                t = template.Template(content, name=self.name)
                content = mark_safe(t.render(context))
            except TemplateSyntaxError as error:
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


def get_filename(page, placeholder, data):
    """
    Generate a stable filename using the orinal filename.
    """
    name_parts = data.name.split('.')
    if len(name_parts) > 1:
        name = slugify('.'.join(name_parts[:-1]), allow_unicode=True)
        ext = slugify(name_parts[-1])
        name = name + '.' + ext
    else:
        name = slugify(data.name)
    filename = os.path.join(
        settings.PAGE_UPLOAD_ROOT,
        'page_' + str(page.id),
        placeholder.ctype + '-' + str(time.time()) + '-' + name
    )
    return filename


class FilePlaceholderNode(PlaceholderNode):
    """A `PlaceholderNode` that saves one file on disk.

    `PAGE_UPLOAD_ROOT` setting define where to save the file.
    """

    def get_field(self, page, language, initial=None):
        help_text = ""
        widget = FileInput(page, language)
        return FileField(
            widget=widget,
            initial=initial,
            help_text=help_text,
            required=False
        )

    def save(self, page, language, data, change, extra_data=None):
        if 'delete' in extra_data:
            return super(FilePlaceholderNode, self).save(
                page,
                language,
                "",
                change
            )
        filename = ''
        if change and data:
            # the image URL is posted if not changed
            if not isinstance(data, UploadedFile):
                return

            filename = get_filename(page, self, data)
            filename = default_storage.save(filename, data)
            return super(FilePlaceholderNode, self).save(
                page,
                language,
                filename,
                change
            )


class ImagePlaceholderNode(FilePlaceholderNode):
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


class ContactForm(forms.Form):
    """
    Simple contact form
    """
    email = forms.EmailField(label=_('Your email'))
    subject = forms.CharField(
        label=_('Subject'), max_length=150)
    message = forms.CharField(
        widget=forms.Textarea(), label=_('Your message'))


class ContactPlaceholderNode(PlaceholderNode):
    """A contact `PlaceholderNode` example."""

    def render(self, context):
        request = context.get('request', None)
        if not request:
            raise ValueError('request not available in the context.')
        if request.method == 'POST':
            form = ContactForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                recipients = [adm[1] for adm in global_settings.ADMINS]
                try:
                    send_mail(
                        data['subject'], data['message'],
                        data['email'], recipients, fail_silently=False)
                    return _("Your email has been sent. Thank you.")
                except:
                    return _("An error as occured: your email has not been sent.")
        else:
            form = ContactForm()
        renderer = render_to_string(
            'pages/contact.html', {'form': form}, RequestContext(request))
        return mark_safe(renderer)


class JsonPlaceholderNode(PlaceholderNode):
    """
    A `PlaceholderNode` that try to return a deserialized JSON object
    in the template.
    """

    def get_render_content(self, context):
        import json
        content = self.get_content_from_context(context)
        try:
            return json.loads(str(content))
        except:
            logger.warning("JsonPlaceholderNode: coudn't decode json")
        return content


class MarkdownPlaceholderNode(PlaceholderNode):
    """
    A `PlaceholderNode` that return HTML from MarkDown format
    """

    widget = Textarea

    def render(self, context):
        """Render markdown."""
        import markdown
        content = self.get_content_from_context(context)
        return markdown.markdown(content)
