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
        
