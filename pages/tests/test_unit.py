# -*- coding: utf-8 -*-
"""Django page CMS unit test suite module."""
from pages.models import Page, Content
from pages.placeholders import PlaceholderNode
from pages.tests.testcase import TestCase, MockRequest
from pages import urlconf_registry as reg
from pages.http import get_language_from_request, get_slug_and_relative_path
from pages.http import get_request_mock

import django
from django.http import Http404
from django.contrib.auth.models import User
from django.conf import settings
from django.template import Template, RequestContext, Context
from django.template.loader import get_template_from_string
from django.template import Template, TemplateSyntaxError

import datetime

class UnitTestCase(TestCase):
    """Django page CMS unit test suite class."""

    def test_date_ordering(self):
        """Test page date ordering feature."""
        from pages import settings as pages_settings
        setattr(pages_settings, "PAGE_USE_SITE_ID", False)
        author = User.objects.all()[0]
        yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
        now = datetime.datetime.now()
        p1 = Page(author=author, status=Page.PUBLISHED, publication_date=now)
        p1.save()
        p2 = Page(
            author=author,
            publication_date=now,
            status=Page.PUBLISHED
        )
        p2.save()
        p3 = Page(
            author=author,
            publication_date=yesterday,
            status=Page.PUBLISHED
        )
        p3.save()

        p2.move_to(p1, position='first-child')
        p3.move_to(p1, position='first-child')

        p1 = Page.objects.get(pk=p1.id)
        p2 = Page.objects.get(pk=p2.id)
        p3 = Page.objects.get(pk=p3.id)
        self.assertEqual(
            [p.id for p in p1.get_children_for_frontend()],
            [p3.id, p2.id]
        )

        self.assertEqual(
            [p.id for p in p1.get_date_ordered_children_for_frontend()],
            [p2.id, p3.id]
        )

    def test_widgets_registry(self):
        """Test the widget registry module."""
        from pages import widgets_registry as wreg
        for widget in wreg.registry:
            w = widget()
            w.render('name', 'value')

        try:
            wreg.register_widget(wreg.registry[0])
            raise AssertionError("Error not raised properly.")
        except wreg.WidgetAlreadyRegistered:
            pass

        try:
            wreg.get_widget('wrong')
            raise AssertionError("Error not raised properly.")
        except wreg.WidgetNotFound:
            pass

    def test_page_caculated_status(self):
        """Test calculated status property."""
        from pages import settings as pages_settings
        setattr(pages_settings, "PAGE_SHOW_START_DATE", True)
        yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
        tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)

        page = self.new_page()
        self.assertEqual(page.calculated_status, Page.PUBLISHED)
        page.publication_date = tomorrow
        self.assertEqual(page.calculated_status, Page.DRAFT)
        page.publication_date = yesterday
        self.assertEqual(page.calculated_status, Page.PUBLISHED)
        setattr(pages_settings, "PAGE_SHOW_END_DATE", True)
        page.publication_end_date = yesterday
        self.assertEqual(page.calculated_status, Page.EXPIRED)

    def test_placeholder_inherit_content(self):
        """Test placeholder content inheritance between pages."""
        from pages import settings as pages_settings
        setattr(pages_settings, "PAGE_USE_SITE_ID", False)
        author = User.objects.all()[0]
        p1 = self.new_page(content={'inher':'parent-content'})
        p2 = self.new_page()
        template = django.template.loader.get_template('pages/tests/test7.html')
        context = Context({'current_page': p2, 'lang':'en-us'})
        self.assertEqual(template.render(context), '')

        p2.move_to(p1, position='first-child')
        self.assertEqual(template.render(context), 'parent-content')

    def test_get_page_template_tag(self):
        """Test get_page template tag."""
        context = Context({})
        pl1 = """{% load pages_tags %}{% get_page get-page-slug as toto %}{{ toto }}"""
        template = get_template_from_string(pl1)
        self.assertEqual(template.render(context), u'None')
        page = self.new_page({'slug':'get-page-slug'})
        self.assertEqual(template.render(context), u'get-page-slug')


    def test_placeholder_all_syntaxes(self):
        """Test placeholder syntaxes."""
        page = self.new_page()
        context = Context({'current_page': page, 'lang':'en-us'})

        pl1 = """{% load pages_tags %}{% placeholder title as hello %}"""
        template = get_template_from_string(pl1)
        self.assertEqual(template.render(context), '')

        pl1 = """{% load pages_tags %}{% placeholder title as hello %}{{ hello }}"""
        template = get_template_from_string(pl1)
        self.assertEqual(template.render(context), page.title())


        # error in parse template content
        setattr(settings, "DEBUG", True)

        page = self.new_page({'wrong': '{% wrong %}'})
        context = Context({'current_page': page, 'lang':'en-us'})

        pl2 = """{% load pages_tags %}{% placeholder wrong parsed %}"""
        template = get_template_from_string(pl2)
        from pages.placeholders import PLACEHOLDER_ERROR
        error = PLACEHOLDER_ERROR % {
            'name': 'wrong',
            'error': "Invalid block tag: 'wrong'",
        }
        self.assertEqual(template.render(context), error)

        # generate errors
        pl3 = """{% load pages_tags %}{% placeholder %}"""
        try:
            template = get_template_from_string(pl3)
        except TemplateSyntaxError:
            pass

        pl4 = """{% load pages_tags %}{% placeholder wrong wrong %}"""
        try:
            template = get_template_from_string(pl4)
        except TemplateSyntaxError:
            pass

        pl5 = """{% load pages_tags %}{% placeholder wrong as %}"""
        try:
            template = get_template_from_string(pl5)
        except TemplateSyntaxError:
            pass

    def test_video(self):
        """Test video placeholder."""
        page = self.new_page(content={
            'title':'video-page',
            'video':'http://www.youtube.com/watch?v=oHg5SJYRHA0\\\\'
        })
        context = Context({'current_page': page, 'lang':'en-us'})
        pl1 = """{% load pages_tags %}{% videoplaceholder video %}"""
        template = get_template_from_string(pl1)
        self.assertNotEqual(template.render(context), '')
        self.assertTrue(len(template.render(context)) > 10)


    def test_placeholder_untranslated_content(self):
        """Test placeholder untranslated content."""
        from pages import settings as pages_settings
        setattr(pages_settings, "PAGE_USE_SITE_ID", False)
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
        context = Context({'current_page': page, 'lang':'en-us'})
        self.assertEqual(template.render(context), '')

    def test_urlconf_registry(self):
        """Test urlconf_registry basic functions."""
        reg.register_urlconf('Documents', 'example.documents.urls',
            label='Display documents')

        reg.get_urlconf('Documents')
        try:
            reg.register_urlconf('Documents', 'example.documents.urls',
            label='Display documents')
        except reg.UrlconfAlreadyRegistered:
            pass
        reg.registry = []
        try:
            reg.get_urlconf('Documents')
        except reg.UrlconfNotFound:
            pass

        reg.register_urlconf('Documents', 'example.documents.urls',
            label='Display documents')

        self.assertEqual(reg.get_choices(),
            [('', 'No delegation'), ('Documents', 'Display documents')])

    def test_permissions(self):
        """Test the permissions lightly."""

        from pages.permissions import PagePermission
        admin = User.objects.get(username='admin')
        page = self.new_page()
        pp = PagePermission(user=page.author)
        self.assertTrue(pp.check('change', page=page, method='GET'))
        self.assertTrue(pp.check('change', page=page, method='POST'))

        staff = User.objects.get(username='staff')
        pp = PagePermission(user=staff)
        # weird because nonstaff?
        self.assertTrue(pp.check('change', page=page, method='GET',
            lang='en-us'))
        self.assertFalse(pp.check('change', page=page, method='POST',
            lang='en-us'))

        self.assertFalse(pp.check('delete', page=page, method='POST',
            lang='en-us'))
        self.assertFalse(pp.check('add', page=page, method='POST',
            lang='en-us'))
        self.assertFalse(pp.check('freeze', page=page, method='POST',
            lang='en-us'))

        self.assertFalse(pp.check('doesnotexist', page=page, method='POST',
            lang='en-us'))

    def test_managers(self):
        Page.objects.populate_pages(child=2, depth=2)
        for p in Page.objects.all():
            p.invalidate()
        self.assertEqual(Page.objects.count(), 3)
        self.assertEqual(Page.objects.published().count(), 3)
        self.assertEqual(Page.objects.drafts().count(), 0)
        self.assertEqual(Page.objects.expired().count(), 0)

    def test_get_content_tag(self):
        """
        Test the {% get_content %} template tag
        """
        page_data = {'title':'test', 'slug':'test'}
        page = self.new_page(page_data)

        context = RequestContext(MockRequest, {'page': page})
        template = Template('{% load pages_tags %}'
                            '{% get_content page "title" "en-us" as content %}'
                            '{{ content }}')
        self.assertEqual(template.render(context), page_data['title'])
        template = Template('{% load pages_tags %}'
                            '{% get_content page "title" as content %}'
                            '{{ content }}')
        self.assertEqual(template.render(context), page_data['title'])

    def test_show_content_tag(self):
        """
        Test the {% show_content %} template tag.
        """
        page_data = {'title':'test', 'slug':'test'}
        page = self.new_page(page_data)
        # cleanup the cache from previous tests
        page.invalidate()

        context = RequestContext(MockRequest, {'page': page, 'lang':'en-us',
            'path':'/page-1/'})
        template = Template('{% load pages_tags %}'
                            '{% show_content page "title" "en-us" %}')
        self.assertEqual(template.render(context), page_data['title'])
        template = Template('{% load pages_tags %}'
                            '{% show_content page "title" %}')
        self.assertEqual(template.render(context), page_data['title'])

    def test_pages_siblings_menu_tag(self):
        """
        Test the {% pages_siblings_menu %} template tag.
        """
        page_data = {'title':'test', 'slug':'test'}
        page = self.new_page(page_data)
        # cleanup the cache from previous tests
        page.invalidate()

        context = RequestContext(MockRequest, {'page': page, 'lang':'en-us',
            'path':'/page-1/'})
        template = Template('{% load pages_tags %}'
                            '{% pages_siblings_menu page %}')
        renderer = template.render(context)

    def test_show_absolute_url_with_language(self):
        """
        Test a {% show_absolute_url %} template tag  bug.
        """
        page_data = {'title':'english', 'slug':'english'}
        page = self.new_page(page_data)
        Content(page=page, language='fr-ch', type='title', body='french').save()
        Content(page=page, language='fr-ch', type='slug', body='french').save()

        self.assertEqual(page.get_url_path(language='fr-ch'), u'/pages/french')
        self.assertEqual(page.get_url_path(language='en-us'), u'/pages/english')

        context = RequestContext(MockRequest, {'page': page})
        template = Template('{% load pages_tags %}'
                            '{% show_absolute_url page "en-us" %}')
        self.assertEqual(template.render(context), u'/pages/english')
        template = Template('{% load pages_tags %}'
                            '{% show_absolute_url page "fr-ch" %}')
        self.assertEqual(template.render(context), u'/pages/french')

    def test_get_page_ids_by_slug(self):
        """
        Test that get_page_ids_by_slug work as intented.
        """
        page_data = {'title':'test1', 'slug':'test1'}
        page1 = self.new_page(page_data)

        self.assertEqual(
            Content.objects.get_page_ids_by_slug('test1'),
            [page1.id]
        )

        page_data = {'title':'test1', 'slug':'test1'}
        page2 = self.new_page(page_data)

        self.assertEqual(
            Content.objects.get_page_ids_by_slug('test1'),
            [page1.id, page2.id]
        )

        Content(page=page1, language='en-us', type='slug', body='test2').save()

        self.assertEqual(
            Content.objects.get_page_ids_by_slug('test1'),
            [page1.id, page2.id]
        )

        Content(page=page1, language='en-us', type='slug', body='test1').save()

        self.assertEqual(
            Content.objects.get_page_ids_by_slug('test1'),
            [page1.id, page2.id]
        )

    def test_get_language_from_request(self):
        """
        Test that get_language_from_request return the default language even if a
        unaccepted language is used.
        """
        class Req():
            LANGUAGE_CODE = 'en-us'
            GET = {}
        request = Req()
        self.assertEqual(
            get_language_from_request(request), 'en-us')

        request.LANGUAGE_CODE = 'dont'
        self.assertEqual(
            get_language_from_request(request), 'en-us')

        request.LANGUAGE_CODE = 'fr-ch'
        self.assertEqual(
            get_language_from_request(request), 'fr-ch')

    def test_get_slug_and_relative_path(self):
        """
        Test that get_slug_and_relative_path doesn't strip the language
        2 times from the path.
        """
        from pages import settings as pages_settings
        old_value = getattr(pages_settings, "PAGE_USE_LANGUAGE_PREFIX")
        setattr(pages_settings, "PAGE_USE_LANGUAGE_PREFIX", True)

        path = 'en-us/path/path/slug'
        slug, path, lang = get_slug_and_relative_path(path)
        self.assertEqual(slug, 'slug')
        self.assertEqual(path, 'path/path/slug')
        self.assertEqual(lang, 'en-us')
        # second pass withe the modified path
        slug, path, lang = get_slug_and_relative_path(path)
        self.assertEqual(slug, 'slug')
        self.assertEqual(path, 'path/path/slug')
        self.assertEqual(lang, None)

        setattr(pages_settings, "PAGE_USE_LANGUAGE_PREFIX", old_value)

    def test_default_view_with_language_prefix(self):
        """
        Test that everything is working with the language prefix option
        activated.
        """
        from pages import settings as pages_settings
        old_value = getattr(pages_settings, "PAGE_USE_LANGUAGE_PREFIX")
        setattr(pages_settings, "PAGE_USE_LANGUAGE_PREFIX", True)

        from pages.views import details
        req = get_request_mock()
        self.assertRaises(Http404, details, req)

        page1 = self.new_page(content={'slug':'page1'})
        page2 = self.new_page(content={'slug':'page2'})

        self.assertEqual(page1.get_url_path(), '/pages/en-us/page1')

        req.path = page1.get_url_path()
        self.assertEqual(details(req, only_context=True)['current_page'],
            page1)

        self.assertEqual(details(req, path=page2.get_complete_slug(),
            only_context=True)['current_page'], page2)

        req.path = page2.get_url_path()
        self.assertEqual(details(req, only_context=True)['current_page'],
            page2)


        setattr(pages_settings, "PAGE_USE_LANGUAGE_PREFIX", old_value)

        req.path = page2.get_url_path()
        self.assertEqual(details(req, only_context=True)['current_page'],
            page2)

