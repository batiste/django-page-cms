# -*- coding: utf-8 -*-
"""Django page CMS command tests suite module."""
from pages.models import Page, Content, PageAlias
from pages.tests.testcase import TestCase
from django.core.management import call_command
from django.test import LiveServerTestCase
import json

class CommandTestCase(TestCase, LiveServerTestCase):
    """Django page CMS command tests suite class."""

    def test_pull(self):
        """Pull command get the correct data"""
        self.new_page(content={'title': 'pull-page', 'slug': 'pull-slug'})
        url =  self.live_server_url + '/pages/api/'
        filename = '/tmp/test'
        call_command('pages_pull', 'admin:b', filename=filename, host=url, verbosity=0)
        with open(filename, "r") as f:
            data = f.read()
            pages = json.loads(data)
            for content in pages[0]['content_set']:
                 self.assertTrue(content['body'] in ['pull-page', 'pull-slug'])

    def test_push(self):
        """Push command put back the content properly"""
        url =  self.live_server_url + '/pages/api/'
        page1 = self.new_page(content={'title': 'pull-page', 'slug': 'pull-slug'})
        page2 = self.new_page(content={'title': 'pull-page-2', 'slug': 'pull-slug-2'})
        call_command('pages_pull', 'admin:b', filename='/tmp/test', host=url, verbosity=0)
        page1.delete()
        self.assertEqual(Page.objects.all().count(), 1)
        call_command('pages_push', 'admin:b', filename='/tmp/test', host=url, verbosity=0)
        self.assertEqual(Page.objects.all().count(), 2)

    def test_tree(self):
        """Push command" restore the tree properly"""
        url =  self.live_server_url + '/pages/api/'
        filename = '/tmp/test'
        page1 = self.new_page(content={'title': 'pull-page-1', 'slug': 'pull-slug-1'})
        page2 = self.new_page(content={'title': 'pull-page-2', 'slug': 'pull-slug-2'}, parent=page1)
        page3 = self.new_page(content={'title': 'pull-page-3', 'slug': 'pull-slug-3'}, parent=page2)

        self.assertSequenceEqual(page1.get_children(), [page2])
        self.assertSequenceEqual(page2.get_children(), [page3])

        call_command('pages_pull', 'admin:b', filename=filename, host=url, verbosity=0)
        page2.move_to(page1, 'left')

        self.assertSequenceEqual(page1.get_children(), [])
        self.assertSequenceEqual(page2.get_children(), [page3])

        call_command('pages_push', 'admin:b', filename='/tmp/test', host=url, verbosity=0)

        self.assertSequenceEqual(page1.get_children(), [page2])
        self.assertSequenceEqual(page2.get_children(), [page3])

    def test_tree_delete(self):
        """Push command tree delete"""
        url =  self.live_server_url + '/pages/api/'
        filename = '/tmp/test'
        page1 = self.new_page(content={'title': 'pull-page-1', 'slug': 'pull-slug-1'})
        page2 = self.new_page(content={'title': 'pull-page-2', 'slug': 'pull-slug-2'}, parent=page1)
        page3 = self.new_page(content={'title': 'pull-page-3', 'slug': 'pull-slug-3'}, parent=page2)

        self.assertSequenceEqual(page1.get_children(), [page2])
        self.assertSequenceEqual(page2.get_children(), [page3])


        call_command('pages_pull', 'admin:b', filename=filename, host=url, verbosity=0)

        page4 = self.new_page(content={'title': 'pull-page-4', 'slug': 'pull-slug-4'}, parent=page1)
        self.assertSequenceEqual(page1.get_children(), [page2, page4])
        page2.delete()
        self.assertSequenceEqual(page1.get_children(), [page4])

        call_command('pages_push', 'admin:b', filename='/tmp/test', host=url, verbosity=0)

        page2 = Page.objects.from_slug('pull-slug-2')
        self.assertSequenceEqual(page1.get_children(), [page4, page2])

