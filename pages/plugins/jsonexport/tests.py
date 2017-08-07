# -*- coding: utf-8 -*-
from django.test.utils import override_settings
from django.contrib.auth.models import User
from taggit.models import Tag

from pages.models import Page
from pages.tests.testcase import TestCase
from pages.plugins.jsonexport.utils import pages_to_json, json_to_pages


class JSONExportTestCase(TestCase):
    """Django page CMS JSON Export tests suite class."""

    @override_settings(PAGE_TAGGING=True)
    def test_flow(self):
        # Export
        page1 = self.new_page(content={'title': 'page1', 'slug': 'slug1'})
        tag1 = Tag.objects.create(name="t1")
        page1.tags.add(tag1)

        page2 = self.new_page(content={'title': 'page2', 'slug': 'slug2'})
        tag2 = Tag.objects.create(name="t2")
        page2.tags.add(tag2)

        data = pages_to_json(Page.objects.all())

        # Clear
        Page.objects.all().delete()
        Tag.objects.all().delete()

        # Import
        user = User.objects.create()
        json_to_pages(data, user)
        pages = Page.objects.all()
        self.assertEqual(pages.count(), 2)

        page1 = Page.objects.from_slug('slug1')
        self.assertEqual(page1.title(), 'page1')
        self.assertEqual([t.name for t in page1.tags.all()], ['t1'])

        page1 = Page.objects.from_slug('slug2')
        self.assertEqual(page1.title(), 'page2')
        self.assertEqual([t.name for t in page1.tags.all()], ['t2'])
