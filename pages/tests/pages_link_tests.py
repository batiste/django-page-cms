# -*- coding: utf-8 -*-
"""Django page CMS test suite module for page links"""
import django
from django.test.client import Client

from pages import settings
from pages.tests.testcase import TestCase
from pages.models import Page, Content, PageAlias

class LinkTestCase(TestCase):
    """Django page CMS link test suite class"""

    def test_01_set_body_pagelink(self):
        """Test the get_body_pagelink_ids and set_body_pagelink functions."""
        setattr(settings, "PAGE_LINK_FILTER", True)
        page1 = self.create_new_page()
        page2 = self.create_new_page()
        # page2 has a link on page1
        content_string = 'test <a href="%s" class="page_%d">hello</a>'
        content = Content(
            page=page2,
            language='en-us',
            type='body',
            body=content_string % ('#', page1.id)
        )
        content.save()
        self.assertEqual(
            Content.objects.get_content(page2, 'en-us', 'body'),
            content_string % (page1.get_absolute_url(), page1.id)
        )
        self.assertFalse(page2.has_broken_link())
        page1.delete()
        self.assertEqual(
            Content.objects.get_content(page2, 'en-us', 'body'),
            'test <a href="#" class="pagelink_broken">hello</a>'
        )
        self.assertTrue(page2.has_broken_link())