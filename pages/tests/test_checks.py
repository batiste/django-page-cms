from pages.checks import page_templates_loading_check

from django.test import TestCase
from django.core.checks import Warning
from django.template import TemplateSyntaxError


class PageTemplatesLoadingCheckTestCase(TestCase):
    def test_check_detects_unexistant_template(self):
        unexistant = ('does_not_exists.html', 'foo')
        with self.settings(PAGE_TEMPLATES=[unexistant]):
            errors = page_templates_loading_check([])

        self.assertEqual(errors, [Warning(
            'Django cannot find template does_not_exists.html',
            obj=unexistant, id='pages.W001')])

    def test_check_doesnt_warn_on_existing_templates(self):
        with self.settings(PAGE_TEMPLATES=[('pages/contact.html', 'bas')]):
            errors = page_templates_loading_check([])

        self.assertEquals(errors, [])

    def test_template_syntax_error_is_not_silenced(self):
        with self.settings(PAGE_TEMPLATES=[('syntax_error.html', 'fail')]):
            with self.assertRaises(TemplateSyntaxError):
                page_templates_loading_check([])
