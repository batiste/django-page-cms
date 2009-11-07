# -*- coding: utf-8 -*-
"""Django page CMS test suite module"""
import django
from django.conf import settings
from django.test.client import Client
from django.template import Template, RequestContext, TemplateDoesNotExist
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response

from pages.models import Page, Content, PageAlias
from pages.tests.testcase import TestCase

class RegressionTestCase(TestCase):
    """Django page CMS test suite class"""

    def test_22_calculated_status_bug(self):
        """
        Test the issue 100
        http://code.google.com/p/django-page-cms/issues/detail?id=100
        """
        setattr(settings, "PAGE_SHOW_START_DATE", True)
        c = Client()
        c.login(username= 'batiste', password='b')
        page_data = self.get_new_page_data()
        page_data['slug'] = 'page1'
        # create a page for the example otherwise you will get a Http404 error
        response = c.post('/admin/pages/page/add/', page_data)
        page1 = Content.objects.get_content_slug_by_slug('page1').page

        page1.status = Page.DRAFT
        page1.save()

        page1.calculated_status
        setattr(settings, "PAGE_SHOW_START_DATE", False)

    def test_23_slug_bug(self):
        """
        Test the issue 97
        http://code.google.com/p/django-page-cms/issues/detail?id=97
        """
        c = Client()
        c.login(username= 'batiste', password='b')
        page_data = self.get_new_page_data()
        page_data['slug'] = 'page1'
        # create a page for the example otherwise you will get a Http404 error
        response = c.post('/admin/pages/page/add/', page_data)

        response = c.get('/pages/page1/')
        self.assertEqual(response.status_code, 200)

        try:
            response = c.get('/pages/toto/page1/')
        except TemplateDoesNotExist, e:
            if e.args != ('404.html',):
                raise

    def test_27_bug_152(self):
        """Test bug 152
        http://code.google.com/p/django-page-cms/issues/detail?id=152"""
        from pages.utils import get_placeholders
        self.assertEqual(
            str(get_placeholders('tests/test1.html')),
            "[<Placeholder Node: body>]"
        )

    def test_28_bug_162(self):
        """Test bug 162
        http://code.google.com/p/django-page-cms/issues/detail?id=162"""
        c = Client()
        c.login(username= 'batiste', password='b')
        page_data = self.get_new_page_data()
        page_data['title'] = 'test-162-title'
        page_data['slug'] = 'test-162-slug'
        response = c.post('/admin/pages/page/add/', page_data)
        self.assertRedirects(response, '/admin/pages/page/')
        from pages.utils import get_request_mock
        request = get_request_mock()
        temp = loader.get_template('tests/test2.html')
        render = temp.render(RequestContext(request, {}))
        self.assertTrue('test-162-slug' in render)

    def test_29_bug_172(self):
        """Test bug 167
        http://code.google.com/p/django-page-cms/issues/detail?id=172"""
        c = Client()
        c.login(username= 'batiste', password='b')
        page_data = self.get_new_page_data()
        page_data['title'] = 'title-en-us'
        page_data['slug'] = 'slug'
        response = c.post('/admin/pages/page/add/', page_data)
        page = Content.objects.get_content_slug_by_slug('slug').page
        Content(page=page, type='title', language='fr-ch',
            body="title-fr-ch").save()

        from pages.utils import get_request_mock
        request = get_request_mock()
        temp = loader.get_template('tests/test3.html')
        render = temp.render(RequestContext(request, {'page':page}))
        self.assertTrue('title-en-us' in render)

        render = temp.render(RequestContext(
            request,
            {'page':page, 'lang':'fr-ch'}
        ))
        self.assertTrue('title-fr-ch' in render)
        

    def test_30_page_id_in_template(self):
        """Get a page in the templates via the page id."""
        page = self.create_new_page()
        from pages.utils import get_request_mock
        request = get_request_mock()
        temp = loader.get_template('tests/test4.html')
        render = temp.render(RequestContext(request, {}))
        self.assertTrue(page.title() in render)

    def test_31_bug_178(self):
        """http://code.google.com/p/django-page-cms/issues/detail?id=178"""
        from pages.utils import get_request_mock
        request = get_request_mock()
        temp = loader.get_template('tests/test5.html')
        render = temp.render(RequestContext(request, {'page':None}))

    def test_32_language_fallback_bug(self):
        """Language fallback doesn't work properly."""
        page = self.create_new_page()
        
        c = Content(page=page, type='new_type', body='toto', language='en-us')
        c.save()

        self.assertEqual(
            Content.objects.get_content(page, 'en-us', 'new_type'),
            'toto'
        )
        self.assertEqual(
            Content.objects.get_content(page, 'fr-ch', 'new_type'),
            ''
        )
        self.assertEqual(
            Content.objects.get_content(page, 'fr-ch', 'new_type', True),
            'toto'
        )

    def test_33_bug_156(self):
        c = Client()
        c.login(username= 'batiste', password='b')
        page_data = self.get_new_page_data()
        page_data['slug'] = 'page1'
        page_data['title'] = 'title &amp;'
        response = c.post('/admin/pages/page/add/', page_data)
        page1 = Content.objects.get_content_slug_by_slug('page1').page
        page1.invalidate()
        c = Content.objects.get_content(page1, 'en-us', 'title')
        self.assertEqual(c, page_data['title'])

    def test_34_bug_181(self):
        c = Client()
        c.login(username= 'batiste', password='b')
        page_data = self.get_new_page_data(draft=True)
        page_data['slug'] = 'page1'
        
        # create a draft page and ensure we can view it
        response = c.post('/admin/pages/page/add/', page_data)
        response = c.get('/pages/page1/')
        self.assertEqual(response.status_code, 200)

        # logout and we should get a 404
        c.logout()
        response = c.get('/pages/page1/')
        self.assertEqual(response.status_code, 404)

        # login as a non staff user and we should get a 404
        c.login(username= 'nonstaff', password='b')
        response = c.get('/pages/page1/')
        self.assertEqual(response.status_code, 404)

        