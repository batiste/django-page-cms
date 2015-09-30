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
        """Pull command"""
        self.new_page(content={'title': 'pull-page', 'slug': 'pull-slug'})
        url =  self.live_server_url + '/pages/api/'
        filename = '/tmp/test'
        call_command('pages_pull', 'admin:b', filename=filename, host=url, verbosity=0)
        with open(filename, "r") as f:
            data = f.read()
            pages = json.loads(data)
            for content in pages['results'][0]['content_set']:
                 self.assertTrue(content['body'] in ['pull-page', 'pull-slug'])

    def test_push(self):
        """Push command"""
        url =  self.live_server_url + '/pages/api/'
        page = self.new_page(content={'title': 'pull-page', 'slug': 'pull-slug'})
        call_command('pages_pull', 'admin:b', filename='/tmp/test', host=url, verbosity=0)
        page.delete()
        self.assertEqual(Page.objects.all().count(), 0)
        call_command('pages_push', 'admin:b', filename='/tmp/test', host=url, verbosity=0)
        self.assertEqual(Page.objects.all().count(), 1)
