# -*- coding: utf-8 -*-
"""Django page CMS test suite module for page links"""
import django
from django.test import TestCase
from pages import settings
from django.test.client import Client

from pages.models import Page, Content, PageAlias
from pages.admin.utils import set_body_pagelink, get_body_pagelink_ids

class LinkTestCase(TestCase):
    """Django page CMS link test suite class"""
    fixtures = ['tests.json']
    counter = 1

    def get_new_page_data(self):
        """Helper method for creating page datas"""
        page_data = {'title':'test page %d' % self.counter, 
            'slug':'test-page-%d' % self.counter, 'language':'en-us',
            'sites':[2], 'status':Page.PUBLISHED,
            # used to disable an error with connected models
            'document_set-TOTAL_FORMS':0, 'document_set-INITIAL_FORMS':0,
            }
        self.counter = self.counter + 1
        return page_data

    def test_01_set_body_pagelink(self):
        """Test the get_body_pagelink_ids and set_body_pagelink ."""
        c = Client()
        
        c.login(username= 'batiste', password='b')
        page_data = self.get_new_page_data()
        response = c.post('/admin/pages/page/add/', page_data)
        slug_content = Content.objects.get_content_slug_by_slug(
            page_data['slug'])
        page1 = slug_content.page
        page_data = self.get_new_page_data()
        response = c.post('/admin/pages/page/add/', page_data)
        slug_content = Content.objects.get_content_slug_by_slug(
            page_data['slug'])
        from pages.utils import get_placeholders
        page2 = slug_content.page
        content_string = 'test <a href="%s" class="page_%d">hello</a>'
        content = Content(
            page=page2,
            language='en-us',
            type='body',
            body=content_string % ('#', page1.id)
        )
        content.save()
        self.assertEqual(get_body_pagelink_ids(page2), [page1.id])

        set_body_pagelink(page2)
        content = Content.objects.filter(
            page=page2, language='en-us', type='body').latest()

        content_string = 'test <a href="%s" class="page_%d" title="%s">hello</a>' \
            % (page1.get_absolute_url(), page1.id, page1.title())
        self.assertEqual(content.body, content_string)

