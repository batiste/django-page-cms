# -*- coding: utf-8 -*-
"""Django page CMS test suite module for page links"""
import django
from django.test.client import Client

from pages import settings
from pages.tests.testcase import TestCase
from pages.models import Page, Content, PageAlias
from pages.admin.utils import set_body_pagelink, get_body_pagelink_ids
from pages.admin.utils import validate_url, update_body_pagelink

class LinkTestCase(TestCase):
    """Django page CMS link test suite class"""

    def test_01_set_body_pagelink(self):
        """Test the get_body_pagelink_ids and set_body_pagelink functions."""
        page1 = self.create_new_page()
        page2 = self.create_new_page()
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

        content = Content.objects.filter(
            page=page2, language='en-us', type='body').latest()

        client = Client()
        client.login(username= 'batiste', password='b')
        response = client.post('/admin/pages/page/%d/move-page/' % page1.id,
            {'position':'first-child', 'target':page2.id})
        page1 = Page.objects.get(id=page1.id)
        self.assertTrue(page1.parent == page2)
        content = Content.objects.filter(
            page=page2, language='en-us', type='body').latest()
        content_string = 'test <a href="%s" class="page_%d" title="%s">hello</a>' \
            % (page1.get_absolute_url(), page1.id, page1.title())
        self.assertEqual(content.body, content_string)
        

    def test_02_valide_url(self):
        self.assertTrue(validate_url(""))
        self.assertTrue(validate_url("http://www.google.com"))
        self.assertFalse(validate_url("http://tot"))
