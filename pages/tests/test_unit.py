# -*- coding: utf-8 -*-
"""Django page CMS unit test suite module."""
from pages.models import Page, Content
from pages.tests.testcase import TestCase
from pages import urlconf_registry as reg
from pages.phttp import get_language_from_request
from pages.phttp import get_request_mock, remove_slug
from pages.utils import get_now
from pages.views import details

from django.http import Http404
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.template import Context
from django.test.utils import override_settings
from taggit.models import Tag

import datetime


class UnitTestCase(TestCase):
    """Django page CMS unit test suite class."""

    def test_date_ordering(self):
        """Test page date ordering feature."""
        self.set_setting("PAGE_USE_SITE_ID", False)
        author = get_user_model().objects.all()[0]
        yesterday = get_now() - datetime.timedelta(days=1)
        now = get_now()
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
        self.set_setting("PAGE_SHOW_START_DATE", True)
        yesterday = get_now() - datetime.timedelta(days=1)
        tomorrow = get_now() + datetime.timedelta(days=1)

        page = self.new_page()
        self.assertEqual(page.calculated_status, Page.PUBLISHED)
        page.publication_date = tomorrow
        self.assertEqual(page.calculated_status, Page.DRAFT)
        page.publication_date = yesterday
        self.assertEqual(page.calculated_status, Page.PUBLISHED)
        self.set_setting("PAGE_SHOW_END_DATE", True)
        page.publication_end_date = yesterday
        self.assertEqual(page.calculated_status, Page.EXPIRED)

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

    def test_get_page_ids_by_slug(self):
        """
        Test that get_page_ids_by_slug work as intented.
        """
        page_data = {'title': 'test1', 'slug': 'test1'}
        page1 = self.new_page(page_data)

        self.assertEqual(
            Content.objects.get_page_ids_by_slug('test1'),
            [page1.id]
        )

        page_data = {'title': 'test1', 'slug': 'test1'}
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

    def test_default_view_with_language_prefix(self):
        """
        Test that everything is working with the language prefix option
        activated.
        """
        self.set_setting("PAGE_USE_LANGUAGE_PREFIX", True)

        from pages.views import details
        req = get_request_mock()
        self.assertRaises(Http404, details, req, '/pages/')

        page1 = self.new_page(content={'slug': 'page1'})
        page2 = self.new_page(content={'slug': 'page2'})

        self.assertEqual(page1.get_url_path(),
            reverse('pages-details-by-path', args=[],
            kwargs={'lang': 'en-us', 'path': 'page1'})
        )

        self.assertEqual(details(req, page1.get_url_path(),
            only_context=True)['current_page'],
            page1)

        self.assertEqual(details(req, path=page2.get_complete_slug(),
            only_context=True)['current_page'], page2)

        self.assertEqual(details(req, page2.get_url_path(),
            only_context=True)['current_page'],
            page2)

        self.set_setting("PAGE_USE_LANGUAGE_PREFIX", False)

        self.assertEqual(details(req, page2.get_url_path(),
            only_context=True)['current_page'],
            page2)

    def test_root_page_hidden_slug(self):
        """
        Check that the root works properly in every case.
        """
        page1 = self.new_page(content={'slug': 'page1'})

        self.set_setting("PAGE_USE_LANGUAGE_PREFIX", False)
        self.set_setting("PAGE_HIDE_ROOT_SLUG", True)
        self.assertEqual(page1.is_first_root(), True)
        self.assertEqual(page1.get_url_path(),
            reverse('pages-details-by-path', args=[], kwargs={'path': ''})
        )

        self.set_setting("PAGE_USE_LANGUAGE_PREFIX", True)
        self.assertEqual(page1.get_url_path(),
            reverse('pages-details-by-path', args=[],
            kwargs={'lang': 'en-us', 'path': ''})
        )

        self.set_setting("PAGE_HIDE_ROOT_SLUG", False)
        page1.invalidate()
        self.assertEqual(page1.get_url_path(),
            reverse('pages-details-by-path', args=[],
            kwargs={'lang': 'en-us', 'path': 'page1'})
        )

        self.set_setting("PAGE_USE_LANGUAGE_PREFIX", False)
        self.assertEqual(page1.get_url_path(),
            reverse('pages-details-by-path', args=[],
            kwargs={'path': 'page1'})
        )

    def test_revision_depth(self):
        """
        Check that PAGE_CONTENT_REVISION_DEPTH works.
        """
        page1 = self.new_page(content={'slug': 'page1'})
        self.set_setting("PAGE_CONTENT_REVISION_DEPTH", 3)
        Content.objects.create_content_if_changed(page1, 'en-us', 'rev-test', 'rev1')
        Content.objects.create_content_if_changed(page1, 'en-us', 'rev-test', 'rev2')
        Content.objects.create_content_if_changed(page1, 'en-us', 'rev-test', 'rev3')
        Content.objects.create_content_if_changed(page1, 'en-us', 'rev-test', 'rev4')
        self.assertEqual(Content.objects.filter(type='rev-test').count(), 3)
        self.assertEqual(
            Content.objects.filter(type='rev-test').latest('creation_date').body,
            'rev4')

    def test_content_dict(self):
        """
        Check that content_dict method works.
        """
        page1 = self.new_page(content={'slug': 'page1'})
        page1.save()
        c = Content.objects.create_content_if_changed(page1, 'en-us', 'body', 'test')
        self.assertEqual(
            page1.content_by_language(language='en-us'),
            [c]
        )

    def test_strict_urls(self):
        """
        Check that the strict handling of URLs work as
        intended.
        """
        page1 = self.new_page(content={'slug': 'page1'})
        page2 = self.new_page(content={'slug': 'page2'})
        page1.save()
        page2.save()
        page2.parent = page1
        page2.save()

        page1 = Page.objects.get(id=page1.id)
        self.assertTrue(page1.get_children(), [page2])

        self.assertEqual(
            Page.objects.from_path('wrong/path/page2', 'en-us'),
            page2
        )

        self.set_setting("PAGE_USE_STRICT_URL", True)

        self.assertEqual(
            Page.objects.from_path('wrong/path/page2', 'en-us'),
            None
        )

        self.assertEqual(
            Page.objects.from_path('page1/page2', 'en-us'),
            page2
        )

    def test_remove_slug(self):
        """Test the remove slug function."""
        self.assertEqual(remove_slug('hello/world/toto'), 'hello/world')
        self.assertEqual(remove_slug('hello/world'), 'hello')
        self.assertEqual(remove_slug('/hello/world/'), 'hello')
        self.assertEqual(remove_slug('hello'), None)

    def test_path_too_long(self):
        """Test that the CMS try to resolve the whole page path to find
        a suitable sub path with delegation."""
        page1 = self.new_page(content={'slug': 'page1'})
        page2 = self.new_page(content={'slug': 'page2'})
        from pages import urlconf_registry as reg
        reg.register_urlconf('test2', 'pages.testproj.documents.urls',
            label='test')
        page2.delegate_to = 'test2'
        page1.delegate_to = 'test2'
        page1.save()
        page2.save()
        page2.parent = page1
        page2.save()

        from pages.testproj.documents.models import Document
        doc = Document(title='doc title 1', text='text', page=page1)
        doc.save()

        req = get_request_mock()
        self.set_setting("PAGE_HIDE_ROOT_SLUG", False)
        page1.invalidate()
        page2.invalidate()

        def _get_context_page(path):
            return details(req, path, 'en-us')
        self.assertEqual(_get_context_page('/').status_code, 200)
        self.assertEqual(_get_context_page('/page1/').status_code, 200)
        self.assertEqual(_get_context_page('/page1/').status_code, 200)
        self.assertEqual(_get_context_page('/page1/page2').status_code, 200)
        self.assertEqual(_get_context_page('/page1/page2/').status_code, 200)
        self.assertEqual(_get_context_page('/page1/page2/doc-%d' % doc.id
            ).status_code, 200)
        self.assertRaises(Http404, _get_context_page,
            '/page1/page-wrong/doc-%d' % doc.id)

        reg.registry = []

    def test_page_methods(self):
        """Test that some methods run properly."""
        page1 = self.new_page(content={'slug': 'page1', 'title': 'hello'})
        page2 = self.new_page(content={'slug': 'page2'})
        page1.save()
        page2.save()
        page2.parent = page1
        page2.save()
        self.assertEqual(
            page1.expose_content(),
            "hello"
        )
        self.assertEqual(
             page2.slug_with_level(),
            "&nbsp;&nbsp;&nbsp;page2"
        )
        p = Page(author=page1.author)
        self.assertEqual(str(p), "Page without id")
        p.save()
        self.assertEqual(str(p), "Page %d" % p.id)

    def test_context_processor(self):
        """Test that the page's context processor is properly activated."""
        from pages.views import details
        req = get_request_mock()
        page1 = self.new_page(content={'slug': 'page1', 'title': 'hello', 'status': 'published'})
        page1.save()
        self.set_setting("PAGES_STATIC_URL", "test_request_context")
        self.assertContains(details(req, path='/'), "test_request_context")

    @override_settings(PAGE_TAGGING=True)
    def test_get_pages_with_tag(self):
        """Test get_pages_with_tag template tag with tag name argument and return a list of pages"""
        page = self.new_page({'slug': 'footer-page', 'somepage': 'get-footer-slug'})
        page2 = self.new_page({'slug': 'footer-page2', 'somepage': 'get-footer-slug'})
        tag = Tag.objects.create(name="footer")
        page.tags.add(tag)
        page2.tags.add(tag)
        pl1 = '{% load pages_tags %}{% get_pages_with_tag "footer" as pages %}' \
              '{% for page in pages %}{{ page.slug }},{% endfor %}'
        template = self.get_template_from_string(pl1)
        self.assertEqual(template.render(Context({})), u'footer-page,footer-page2,')
