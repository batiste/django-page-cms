# -*- coding: utf-8 -*-
"""Django page CMS unit test suite module."""
from pages.models import Page, Content
from pages.plugins.category.models import Category
from pages.placeholders import PlaceholderNode, get_filename
from pages.tests.testcase import TestCase, MockRequest
from pages import urlconf_registry as reg
from pages.http import get_language_from_request, get_slug
from pages.http import get_request_mock, remove_slug
from pages.utils import export_po_files, import_po_files, get_now
from pages.views import details
from pages.templatetags.pages_tags import get_page_from_string_or_id

import django
import unittest
from django.http import Http404
from django.contrib.auth.models import User
from django.conf import settings
from django.core.urlresolvers import reverse
from django.template import Template, RequestContext, Context
from django.template.loader import get_template_from_string
from django.template import Template, TemplateSyntaxError

import datetime

class UnitTestCase(TestCase):
    """Django page CMS unit test suite class."""

    def test_date_ordering(self):
        """Test page date ordering feature."""
        self.set_setting("PAGE_USE_SITE_ID", False)
        author = User.objects.all()[0]
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

    def test_placeholder_inherit_content(self):
        """Test placeholder content inheritance between pages."""
        self.set_setting("PAGE_USE_SITE_ID", False)
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
        pl1 = """{% load pages_tags %}{% get_page "get-page-slug" as toto %}{{ toto }}"""
        template = get_template_from_string(pl1)
        self.assertEqual(template.render(context), u'None')
        page = self.new_page({'slug': 'get-page-slug'})
        self.assertEqual(template.render(context), u'get-page-slug')

    def test_get_pages_for_category_template_tag(self):
        category = self.new_category()
        content = {
            'title': 'test-page',
            'category': category.slug,
        }
        pages = [self.new_page(content=content) for i in xrange(3)]
        tpl = """{% load pages_tags %}{% pages_for_category 'test-category' %}{% for page in pages %}{{ page.title }}
        {% endfor %}"""
        template = get_template_from_string(tpl)
        out = template.render(Context({}))
        easy_out = out.strip().replace('\n', '').replace(8 * ' ', ' ')
        self.assertEqual(easy_out, 'test-page test-page test-page')

    def test_placeholder_all_syntaxes(self):
        """Test placeholder syntaxes."""
        page = self.new_page()
        context = Context({'current_page': page, 'lang': 'en-us'})

        pl1 = """{% load pages_tags %}{% placeholder title as hello %}"""
        template = get_template_from_string(pl1)
        self.assertEqual(template.render(context), '')

        pl1 = """{% load pages_tags %}{% placeholder title as hello %}{{ hello }}"""
        template = get_template_from_string(pl1)
        self.assertEqual(template.render(context), page.title())


        # to be sure to raise an errors in parse template content
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


    def test_placeholder_quoted_name(self):
        """Test placeholder name with quotes."""
        page = self.new_page()
        context = Context({'current_page': page, 'lang': 'en-us'})
        placeholder = PlaceholderNode("test name")
        placeholder.save(page, 'en-us', 'some random value', False)

        pl1 = """{% load pages_tags %}{% placeholder "test name" as hello %}{{ hello }}"""
        template = get_template_from_string(pl1)
        self.assertEqual(template.render(context), 'some random value')

        placeholder = PlaceholderNode("with accent éàè")
        placeholder.save(page, 'en-us', 'some random value', False)

        pl1 = """{% load pages_tags %}{% placeholder "with accent éàè" as hello %}{{ hello }}"""
        template = get_template_from_string(pl1)
        self.assertEqual(template.render(context), 'some random value')


    def test_parsed_template(self):
        """Test the parsed template syntax."""
        setattr(settings, "DEBUG", True)
        page = self.new_page({'title':'<b>{{ "hello"|capfirst }}</b>'})
        page.save()
        context = Context({'current_page': page, 'lang':'en-us'})
        pl_parsed = """{% load pages_tags %}{% placeholder title parsed %}"""
        template = get_template_from_string(pl_parsed)
        self.assertEqual(template.render(context), '<b>Hello</b>')
        setattr(settings, "DEBUG", False)
        page = self.new_page({'title':'<b>{{ "hello"|wrong_filter }}</b>'})
        context = Context({'current_page': page, 'lang':'en-us'})
        self.assertEqual(template.render(context), u'')


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

        self.assertFalse(pp.check('publish', page=page, method='POST',
            lang='en-us'))

    def test_managers(self):
        # TODO: this test seems dependant from other tests
        self.set_setting("PAGE_USE_SITE_ID", False)
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
        page_data = {'title': 'test', 'slug': 'test'}
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
        context = RequestContext(MockRequest, {'page': page})
        template = Template('{% load pages_tags %}'
                            '{% get_content page "slug" as content %}'
                            '{{ content }}')
        self.assertEqual(template.render(context), 'english')

        # french specified
        context = RequestContext(MockRequest, {'page': page, 'lang': 'fr'})
        template = Template('{% load pages_tags %}'
                            '{% get_content page "slug" as content %}'
                            '{{ content }}')
        self.assertEqual(template.render(context), 'french')

        # english specified
        context = RequestContext(MockRequest, {'page': page, 'lang': 'en-us'})
        template = Template('{% load pages_tags %}'
                            '{% get_content page "slug" as content %}'
                            '{{ content }}')
        self.assertEqual(template.render(context), 'english')

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
        page_data = {'title': 'english', 'slug': 'english'}
        page = self.new_page(page_data)
        Content(page=page, language='fr-ch', type='title', body='french').save()
        Content(page=page, language='fr-ch', type='slug', body='french').save()

        self.assertEqual(page.get_url_path(language='fr-ch'),
            self.get_page_url(u'french'))
        self.assertEqual(page.get_url_path(language='en-us'),
            self.get_page_url(u'english'))

        context = RequestContext(MockRequest, {'page': page})
        template = Template('{% load pages_tags %}'
                            '{% show_absolute_url page "en-us" %}')
        self.assertEqual(template.render(context),
            self.get_page_url(u'english'))
        template = Template('{% load pages_tags %}'
                            '{% show_absolute_url page "fr-ch" %}')
        self.assertEqual(template.render(context),
            self.get_page_url('french'))

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
        page1 = self.new_page(content={'slug':'page1'})
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
        page1 = self.new_page(content={'slug':'page1'})
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
        page1 = self.new_page(content={'slug':'page1'})
        page2 = self.new_page(content={'slug':'page2'})
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
        page1 = self.new_page(content={'slug':'page1'})
        page2 = self.new_page(content={'slug':'page2'})
        from pages import urlconf_registry as reg
        reg.register_urlconf('test', 'pages.testproj.documents.urls',
            label='test')
        page2.delegate_to = 'test'
        page1.delegate_to = 'test'
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

    def test_po_file_imoprt_export(self):
        """Test the po files export and import."""
        try:
            import polib
        except ImportError:
            raise unittest.SkipTest("Polib is not installed")

        page1 = self.new_page(content={'slug':'page1', 'title':'english title'})
        page1.save()
        #Content(page=page1, language='en-us', type='title', body='toto').save()
        Content(page=page1, language='fr-ch', type='title', body='french title').save()
        page1.invalidate()

        import StringIO
        stdout = StringIO.StringIO()

        # TODO: might be nice to use a temp dir for this test
        export_po_files(path='potests', stdout=stdout)
        self.assertTrue("Export language fr-ch" in stdout.getvalue())

        f = open("potests/fr-ch.po", "r+")
        old = f.read().replace('french title', 'translated')
        f.seek(0)
        f.write(old)
        f.close()

        stdout = StringIO.StringIO()
        import_po_files(path='potests', stdout=stdout)

        self.assertTrue("Update language fr-ch" in stdout.getvalue())
        self.assertTrue(("Update page %d" % page1.id) in stdout.getvalue())
        self.assertTrue(page1.title(language='fr-ch'), 'translated')

    def test_page_methods(self):
        """Test that some methods run properly."""
        page1 = self.new_page(content={'slug': 'page1', 'title':'hello'})
        page2 = self.new_page(content={'slug': 'page2'})
        page1.save()
        page2.save()
        page2.parent = page1
        page2.save()
        self.assertEqual(
            page1.expose_content(),
            u"hello"
        )
        self.assertEqual(
             page2.slug_with_level(),
            u"&nbsp;&nbsp;&nbsp;page2"
        )
        p = Page(author=page1.author)
        self.assertEqual(unicode(p), u"Page without id")
        p.save()
        self.assertEqual(unicode(p), u"Page %d" % p.id)

    def test_context_processor(self):
        """Test that the page's context processor is properly activated."""
        from pages.views import details
        req = get_request_mock()
        page1 = self.new_page(content={'slug': 'page1', 'title': 'hello'})
        page1.save()
        self.set_setting("PAGES_MEDIA_URL", "test_request_context")
        self.assertContains(details(req, path='/'), "test_request_context")

    def test_get_page_from_id_context_variable(self):
        """Test get_page_from_string_or_id with an id context variable."""
        page = self.new_page({'slug': 'test'})
        self.assertEqual(get_page_from_string_or_id(unicode(page.id)), page)

        content = Content(page=page, language='en-us', type='test_id',
            body=page.id)
        content.save()
        context = Context({'current_page': page})
        context = RequestContext(MockRequest, context)
        template = Template('{% load pages_tags %}'
                            '{% placeholder test_id as str %}'
                            '{% get_page str as p %}'
                            '{{ p.slug }}')
        self.assertEqual(template.render(context), 'test')

    def test_get_page_from_slug_context_variable(self):
        """Test get_page_from_string_or_id with an slug context variable."""
        page = self.new_page({'slug': 'test'})

        context = Context({'current_page': page})
        context = RequestContext(MockRequest, context)
        template = Template('{% load pages_tags %}'
                            '{% placeholder slug as str %}'
                            '{% get_page str as p %}'
                            '{{ p.slug }}')
        self.assertEqual(template.render(context), 'test')

        template = Template('{% load pages_tags %}'
                            '{% get_page "test" as p %}'
                            '{{ p.slug }}')
        self.assertEqual(template.render(context), 'test')

    def test_get_page_template_tag_with_page_arg_as_id(self):
        """Test get_page template tag with page argument given as a page id"""
        context = Context({})
        pl1 = """{% load pages_tags %}{% get_page 1 as toto %}{{ toto }}"""
        template = get_template_from_string(pl1)
        page = self.new_page({'id': 1, 'slug': 'get-page-slug'})
        self.assertEqual(template.render(context), u'get-page-slug')

    def test_get_page_template_tag_with_variable_containing_page_id(self):
        """Test get_page template tag with page argument given as a page id"""
        context = Context({})
        pl1 = ('{% load pages_tags %}{% placeholder somepage as page_id %}'
            '{% get_page page_id as toto %}{{ toto }}')
        template = get_template_from_string(pl1)
        page = self.new_page({'id': 1, 'slug': 'get-page-slug',
            'somepage': '1'})
        context = Context({'current_page': page})
        self.assertEqual(template.render(context), u'get-page-slug')

    def test_get_page_template_tag_with_variable_containing_page_slug(self):
        """Test get_page template tag with page argument given as a page id"""
        context = Context({})
        pl1 = ('{% load pages_tags %}{% placeholder somepage as slug %}'
            '{% get_page slug as toto %}{{ toto }}')
        template = get_template_from_string(pl1)
        page = self.new_page({'slug': 'get-page-slug', 'somepage':
            'get-page-slug' })
        context = Context({'current_page': page})
        self.assertEqual(template.render(context), u'get-page-slug')

    def test_variable_disapear_in_block(self):
        """Try to test the disapearance of a context variable in a block."""
        tpl = ("{% load pages_tags %}"
          "{% placeholder slug as test_value untranslated %}"
          "{% block someblock %}"
          "{% get_page test_value as toto %}"
          "{{ toto.slug }}"
          "{% endblock %}")

        template = get_template_from_string(tpl)
        page = self.new_page({'slug': 'get-page-slug'})
        context = Context({'current_page': page})
        self.assertEqual(template.render(context), u'get-page-slug')

    def test_get_filename(self):
        placeholder = PlaceholderNode("placeholdername")
        page = self.new_page({'slug': 'page1'})
        data = "myfile.pdf"
        self.assertTrue(data in get_filename(page, placeholder, data))
        self.assertTrue("page_%d" % page.id in get_filename(page, placeholder, data))
        self.assertTrue(placeholder.name in get_filename(page, placeholder, data))

    def test_get_category_name(self):
        tpl = """{% load pages_tags %}{% category_name 'test-category' %}"""
        template = get_template_from_string(tpl)
        category = self.new_category()
        context = Context({})
        self.assertEqual(template.render(context), 'Test category')

    def test_get_invalid_category_name(self):
        tpl = """{% load pages_tags %}{% category_name 'enoent' %}"""
        template = get_template_from_string(tpl)
        category = self.new_category()
        context = Context({})
        self.assertEqual(template.render(context), '')

    def test_get_category(self):
        tpl = """{% load pages_tags %}{% get_category 'test-category' %}{{ category.title }}"""
        template = get_template_from_string(tpl)
        category = self.new_category()
        context = Context({})
        self.assertEqual(template.render(context), 'Test category')

    def test_get_invalidcategory(self):
        tpl = """{% load pages_tags %}{% get_category 'enoent' %}{{ category.title }}"""
        template = get_template_from_string(tpl)
        category = self.new_category()
        context = Context({})
        self.assertEqual(template.render(context), 'Enoent')

