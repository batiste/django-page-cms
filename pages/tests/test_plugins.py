# -*- coding: utf-8 -*-
"""Django page CMS plugin test suite module."""
from pages.tests.testcase import TestCase
from pages.plugins.jsonexport import utils
from pages.models import Page
import json
from pages.plugins.jsonexport.tests import JSONExportTestCase


class Dummy(JSONExportTestCase):
    pass


class PluginTestCase(TestCase):
    """Django page CMS plugin tests."""

    def test_json_parsing(self):
        """Test page date ordering feature."""
        self.new_page({'slug': 'p1'})
        self.new_page({'slug': 'p2'})
        jsondata = utils.pages_to_json(Page.objects.all())

        self.assertIn("p1", jsondata)
        self.assertIn("p2", jsondata)
        data = json.loads(jsondata)
        self.assertEqual(len(data['pages']), 2)
