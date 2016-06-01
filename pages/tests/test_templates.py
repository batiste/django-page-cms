# -*- coding: utf-8 -*-
"""Django page CMS template test suite module."""
from pages.models import Content
from pages.placeholders import PlaceholderNode, get_filename
from pages.tests.testcase import TestCase, MockRequest
from pages.templatetags.pages_tags import get_page_from_string_or_id
from pages.phttp import get_request_mock

import django
import six

from django.template import Template, Context, TemplateSyntaxError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings


def render(template, context):
    return template.render(Context(context))


class TemplateTestCase(TestCase):
    """Django page CMS unit test suite class."""

    def test_placeholder_inherit_content(self):
        """Test placeholder content inheritance between pages."""
        self.set_setting("PAGE_USE_SITE_ID", False)
        p1 = self.new_page(content={'inher': 'parent-content'})
        p2 = self.new_page()
        template = django.template.loader.get_template('pages/tests/test7.html')
        context = {'current_page': p2, 'lang': 'en-us'}
        self.assertEqual(render(template, context), '')

        p2.move_to(p1, position='first-child')
        self.assertEqual(render(template, context), 'parent-content')

    def test_get_page_template_tag(self):
        """Test get_page template tag."""
        context = {}
        pl1 = """{% load pages_tags %}{% get_page "get-page-slug" as toto %}{{ toto }}"""
        template = self.get_template_from_string(pl1)
        self.assertEqual(render(template, context), 'None')
        self.new_page({'slug': 'get-page-slug'})
        self.assertEqual(render(template, context), 'get-page-slug')

    def test_placeholder_all_syntaxes(self):
        """Test placeholder syntaxes."""
        page = self.new_page()
        context = {'current_page': page, 'lang': 'en-us'}

        pl1 = """{% load pages_tags %}{% placeholder title as hello %}"""
        template = self.get_template_from_string(pl1)
        self.assertEqual(render(template, context), '')

        pl1 = """{% load pages_tags %}{% placeholder title as hello %}{{ hello }}"""
        template = self.get_template_from_string(pl1)
        self.assertEqual(render(template, context), page.title())

        # to be sure to raise an errors in parse template content
        setattr(settings, "DEBUG", True)

        page = self.new_page({'wrong': '{% wrong %}'})
        context = {'current_page': page, 'lang': 'en-us'}

        pl2 = """{% load pages_tags %}{% placeholder wrong parsed %}"""
        template = self.get_template_from_string(pl2)
        from pages.placeholders import PLACEHOLDER_ERROR
        # There are diffrence in errors in each Django so check each
        error18 = PLACEHOLDER_ERROR % {
            'name': 'wrong',
            'error': "Invalid block tag: 'wrong'",
        }
        error19 = PLACEHOLDER_ERROR % {
            'name': 'wrong',
            'error': "Invalid block tag on line 1: 'wrong'. Did you forget to register or load this tag?",
        }
        rendered_error = render(template, context)
        self.assertIn(rendered_error, [error18, error19])

        # generate errors
        pl3 = """{% load pages_tags %}{% placeholder %}"""
        try:
            template = self.get_template_from_string(pl3)
        except TemplateSyntaxError:
            pass

        pl4 = """{% load pages_tags %}{% placeholder wrong wrong %}"""
        try:
            template = self.get_template_from_string(pl4)
        except TemplateSyntaxError:
            pass

        pl5 = """{% load pages_tags %}{% placeholder wrong as %}"""
        try:
            template = self.get_template_from_string(pl5)
        except TemplateSyntaxError:
            pass

    def test_placeholder_quoted_name(self):
        """Test placeholder name with quotes."""
        page = self.new_page()
        context = {'current_page': page, 'lang': 'en-us'}
        placeholder = PlaceholderNode("test name")
        placeholder.save(page, 'en-us', 'some random value', False)

        pl1 = """{% load pages_tags %}{% placeholder "test name" as hello %}{{ hello }}"""
        template = self.get_template_from_string(pl1)
        self.assertEqual(render(template, context), 'some random value')

        placeholder = PlaceholderNode("with accent éàè")
        placeholder.save(page, 'en-us', 'some random value', False)

        pl1 = """{% load pages_tags %}{% placeholder "with accent éàè" as hello %}{{ hello }}"""
        template = self.get_template_from_string(pl1)
        self.assertEqual(render(template, context), 'some random value')

    def test_parsed_template(self):
        """Test the parsed template syntax."""
        setattr(settings, "DEBUG", True)
        page = self.new_page({'title': '<b>{{ "hello"|capfirst }}</b>'})
        page.save()
        context = {'current_page': page, 'lang': 'en-us'}
        pl_parsed = """{% load pages_tags %}{% placeholder title parsed %}"""
        template = self.get_template_from_string(pl_parsed)
        self.assertEqual(render(template, context), '<b>Hello</b>')
        setattr(settings, "DEBUG", False)
        page = self.new_page({'title': '<b>{{ "hello"|wrong_filter }}</b>'})
        context = {'current_page': page, 'lang': 'en-us'}
        self.assertEqual(render(template, context), '')

    def test_placeholder_untranslated_content(self):
        """Test placeholder untranslated content."""
        self.set_setting("PAGE_USE_SITE_ID", False)
        page = self.new_page(content={})
        placeholder = PlaceholderNode('untrans', page='p', untranslated=True)
        placeholder.save(page, 'fr-ch', 'test-content', True)
        placeholder.save(page, 'en-us', 'test-content', True)
        self.assertEqual(len(Content.objects.all()), 1)
        self.assertEqual(Content.objects.all()[0].language, 'en-us')

        placeholder = PlaceholderNode('untrans', page='p', untranslated=False)
        placeholder.save(page, 'fr-ch', 'test-content', True)
        self.assertEqual(len(Content.objects.all()), 2)

        # test the syntax
        page = self.new_page()
        template = django.template.loader.get_template(
                'pages/tests/untranslated.html')
        context = {'current_page': page, 'lang': 'en-us'}
        self.assertEqual(render(template, context), '')

    def test_get_content_tag(self):
        """
        Test the {% get_content %} template tag
        """
        page_data = {'title': 'test', 'slug': 'test'}
        page = self.new_page(page_data)

        context = {'page': page}
        template = Template('{% load pages_tags %}'
                            '{% get_content page "title" "en-us" as content %}'
                            '{{ content }}')
        self.assertEqual(render(template, context), page_data['title'])
        template = Template('{% load pages_tags %}'
                            '{% get_content page "title" as content %}'
                            '{{ content }}')
        self.assertEqual(render(template, context), page_data['title'])

    def test_get_content_tag_bug(self):
        """
        Make sure that {% get_content %} use the "lang" context variable if
        no language string is provided.
        """
        page_data = {'title': 'test', 'slug': 'english'}
        page = self.new_page(page_data)
        Content(page=page, language='fr-ch', type='title', body='french').save()
        Content(page=page, language='fr-ch', type='slug', body='french').save()
        self.assertEqual(page.slug(language='fr-ch'), 'french')
        self.assertEqual(page.slug(language='en-us'), 'english')

        # default
        context = {'page': page}
        template = Template('{% load pages_tags %}'
                            '{% get_content page "slug" as content %}'
                            '{{ content }}')
        self.assertEqual(render(template, context), 'english')

        # french specified
        context = {'page': page, 'lang': 'fr'}
        template = Template('{% load pages_tags %}'
                            '{% get_content page "slug" as content %}'
                            '{{ content }}')
        self.assertEqual(render(template, context), 'french')

        # english specified
        context = {'page': page, 'lang': 'en-us'}
        template = Template('{% load pages_tags %}'
                            '{% get_content page "slug" as content %}'
                            '{{ content }}')
        self.assertEqual(render(template, context), 'english')

    def test_show_content_tag(self):
        """
        Test the {% show_content %} template tag.
        """
        page_data = {'title': 'test', 'slug': ' test'}
        page = self.new_page(page_data)
        # cleanup the cache from previous tests
        page.invalidate()

        context = {'page': page, 'lang': 'en-us', 'path': '/page-1/'}
        template = Template('{% load pages_tags %}'
                            '{% show_content page "title" "en-us" %}')
        self.assertEqual(render(template, context), page_data['title'])
        template = Template('{% load pages_tags %}'
                            '{% show_content page "title" %}')
        self.assertEqual(render(template, context), page_data['title'])

    def test_pages_siblings_menu_tag(self):
        """
        Test the {% pages_siblings_menu %} template tag.
        """
        page_data = {'title': 'test', 'slug': 'test'}
        page = self.new_page(page_data)
        # cleanup the cache from previous tests
        page.invalidate()

        context = {'page': page, 'lang': 'en-us', 'path': '/page-1/'}
        template = Template('{% load pages_tags %}'
                            '{% pages_siblings_menu page %}')
        render(template, context)

    def test_admin_menu_tag(self):
        """
        Test the {% pages_admin_menu %} template tag with cookies.
        """
        page_data = {'title': 'test', 'slug': 'test'}
        page = self.new_page(page_data)
        # cleanup the cache from previous tests
        page.invalidate()

        # TODO: need fixing
        request = MockRequest()
        request.COOKIES['tree_expanded'] = "%d,10,20" % page.id
        context = {'page': page, 'lang': 'en-us', 'path': '/page-1/'}
        template = Template('{% load pages_tags %}'
                            '{% pages_admin_menu page %}')
        render(template, context)

    def test_show_absolute_url_with_language(self):
        """
        Test a {% show_absolute_url %} template tag  bug.
        """
        page_data = {'title': 'english', 'slug': 'english'}
        page = self.new_page(page_data)
        Content(page=page, language='fr-ch', type='title', body='french').save()
        Content(page=page, language='fr-ch', type='slug', body='french').save()

        self.assertEqual(page.get_url_path(language='fr-ch'),
            self.get_page_url('french'))
        self.assertEqual(page.get_url_path(language='en-us'),
            self.get_page_url('english'))

        context = {'page': page}
        template = Template('{% load pages_tags %}'
                            '{% show_absolute_url page "en-us" %}')
        self.assertEqual(render(template, context),
            self.get_page_url('english'))
        template = Template('{% load pages_tags %}'
                            '{% show_absolute_url page "fr-ch" %}')
        self.assertEqual(render(template, context),
            self.get_page_url('french'))

    def test_get_page_from_id_context_variable(self):
        """Test get_page_from_string_or_id with an id context variable."""
        page = self.new_page({'slug': 'test'})
        self.assertEqual(get_page_from_string_or_id(str(page.id)), page)

        content = Content(page=page, language='en-us', type='test_id',
            body=page.id)
        content.save()
        context = {'current_page': page}
        template = Template('{% load pages_tags %}'
                            '{% placeholder test_id as str %}'
                            '{% get_page str as p %}'
                            '{{ p.slug }}')
        self.assertEqual(render(template, context), 'test')

    def test_get_page_from_slug_context_variable(self):
        """Test get_page_from_string_or_id with an slug context variable."""
        page = self.new_page({'slug': 'test'})

        context = {'current_page': page}
        template = Template('{% load pages_tags %}'
                            '{% placeholder slug as str %}'
                            '{% get_page str as p %}'
                            '{{ p.slug }}')
        self.assertEqual(render(template, context), 'test')

        template = Template('{% load pages_tags %}'
                            '{% get_page "test" as p %}'
                            '{{ p.slug }}')
        self.assertEqual(render(template, context), 'test')

    def test_get_page_template_tag_with_page_arg_as_id(self):
        """Test get_page template tag with page argument given as a page id"""
        context = {}
        pl1 = """{% load pages_tags %}{% get_page 1 as toto %}{{ toto }}"""
        template = self.get_template_from_string(pl1)
        self.new_page({'id': 1, 'slug': 'get-page-slug'})
        self.assertEqual(render(template, context), 'get-page-slug')

    def test_get_page_template_tag_with_variable_containing_page_id(self):
        """Test get_page template tag with page argument given as a page id"""
        context = {}
        pl1 = ('{% load pages_tags %}{% placeholder somepage as page_id %}'
            '{% get_page page_id as toto %}{{ toto }}')
        template = self.get_template_from_string(pl1)
        page = self.new_page({'id': 1, 'slug': 'get-page-slug',
            'somepage': '1'})
        context = {'current_page': page}
        self.assertEqual(render(template, context), 'get-page-slug')

    def test_get_page_template_tag_with_variable_containing_page_slug(self):
        """Test get_page template tag with page argument given as a page id"""
        context = {}
        pl1 = ('{% load pages_tags %}{% placeholder somepage as slug %}'
            '{% get_page slug as toto %}{{ toto }}')
        template = self.get_template_from_string(pl1)
        page = self.new_page({'slug': 'get-page-slug', 'somepage':
            'get-page-slug'})
        context = {'current_page': page}
        self.assertEqual(render(template, context), 'get-page-slug')

    def test_variable_disapear_in_block(self):
        """Try to test the disapearance of a context variable in a block."""
        tpl = ("{% load pages_tags %}"
          "{% placeholder slug as test_value untranslated %}"
          "{% block someblock %}"
          "{% get_page test_value as toto %}"
          "{{ toto.slug }}"
          "{% endblock %}")

        template = self.get_template_from_string(tpl)
        page = self.new_page({'slug': 'get-page-slug'})
        context = {'current_page': page}
        self.assertEqual(render(template, context), 'get-page-slug')

    def test_get_filename(self):
        placeholder = PlaceholderNode("placeholdername")
        page = self.new_page({'slug': 'page1'})
        fakefile = SimpleUploadedFile(name=u"some {}[]@$%*()+myfile.pdf", content=six.b('bytes'))
        filename = get_filename(page, placeholder, fakefile)
        self.assertTrue('some-myfile.pdf' in filename)
        self.assertTrue("page_%d" % page.id in filename)
        self.assertTrue(placeholder.name in filename)

    def test_get_filename_edge_case(self):
        placeholder = PlaceholderNode("placeholdername")
        page = self.new_page({'slug': 'page1'})
        fakefile = SimpleUploadedFile(name=u"hello<script>world", content=six.b('bytes'))
        filename = get_filename(page, placeholder, fakefile)
        self.assertNotIn('<', filename)

    def test_json_placeholder(self):
        tpl = ("{% load pages_tags %}{% jsonplaceholder p1 as v %}{{ v.a }}")

        template = self.get_template_from_string(tpl)
        page = self.new_page({'p1': '{"a":1}'})
        context = {'current_page': page}
        self.assertEqual(render(template, context), '1')

        tpl = ("{% load pages_tags %}{% jsonplaceholder p1 %}")
        template = self.get_template_from_string(tpl)
        page = self.new_page({'p1': 'wrong'})
        context = {'current_page': page}
        self.assertEqual(render(template, context), 'wrong')

    def test_file_placeholder(self):
        tpl = ("{% load pages_tags %}{% fileplaceholder f1 %}")

        template = self.get_template_from_string(tpl)
        page = self.new_page({'f1': 'filename'})
        context = {'current_page': page}
        self.assertEqual(render(template, context), 'filename')

    def test_image_placeholder(self):
        tpl = ("{% load pages_tags %}{% imageplaceholder f1 %}")

        template = self.get_template_from_string(tpl)
        page = self.new_page({'f1': 'filename'})
        context = {'current_page': page}
        self.assertEqual(render(template, context), 'filename')

    def test_contact_placeholder(self):
        tpl = ("{% load pages_tags %}{% contactplaceholder contact %}")

        template = self.get_template_from_string(tpl)
        page = self.new_page({'contact': 'hello'})
        context = {'current_page': page}

        import logging
        logger = logging.getLogger("pages")
        lvl = logger.getEffectiveLevel()
        logger.setLevel(logging.ERROR)

        with self.assertRaises(ValueError):
            self.assertEqual(render(template, context), 'hello')

        logger.setLevel(lvl)

        context = {'current_page': page, 'request': get_request_mock()}
        self.assertTrue("<form" in render(template, context))

    def test_placeholder_section(self):
        tpl = ("{% load pages_tags %}{% placeholder 'meta_description' section 'SEO Options' %}")

        template = self.get_template_from_string(tpl)
        found = False
        for node in template.nodelist:
            if isinstance(node, PlaceholderNode):
                found = True
                self.assertEqual(node.section, 'SEO Options')
        self.assertTrue(found)

        page = self.new_page({'meta_description': 'foo'})
        context = {'current_page': page, 'request': get_request_mock()}
        self.assertTrue("foo" in render(template, context))
