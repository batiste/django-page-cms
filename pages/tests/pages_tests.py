# -*- coding: utf-8 -*-
"""Django page CMS unit test suite module."""
from pages.models import Page, Content, PageAlias
from pages.placeholders import PlaceholderNode
from pages.tests.testcase import TestCase
from pages import urlconf_registry as reg

import django
from django.contrib.auth.models import User
from django.conf import settings
from django.template import Template, RequestContext, Context

import datetime

class PagesTestCase(TestCase):
    """Django page CMS unit test suite class."""

    def test_date_ordering(self):
        """Test page date ordering feature."""
        from pages import settings as pages_settings
        setattr(pages_settings, "PAGE_USE_SITE_ID", False)
        author = User.objects.all()[0]
        yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
        now = datetime.datetime.now()
        p1 = Page(author=author, status=Page.PUBLISHED, publication_date=now)
        p1.save()
        p2 = Page(
            author=author,
            publication_date=now,
            status=Page.PUBLISHED
        )
        p2.save()
        p3 = Page(
            author=author,
            publication_date=yesterday,
            status=Page.PUBLISHED
        )
        p3.save()

        p2.move_to(p1, position='first-child')
        p3.move_to(p1, position='first-child')

        p1 = Page.objects.get(pk=p1.id)
        p2 = Page.objects.get(pk=p2.id)
        p3 = Page.objects.get(pk=p3.id)
        self.assertEqual(
            [p.id for p in p1.get_children_for_frontend()],
            [p3.id, p2.id]
        )

        self.assertEqual(
            [p.id for p in p1.get_date_ordered_children_for_frontend()],
            [p2.id, p3.id]
        )

    def test_placeholder_inherit_content(self):
        """Test placeholder content inheritance between pages."""
        from pages import settings as pages_settings
        setattr(pages_settings, "PAGE_USE_SITE_ID", False)
        author = User.objects.all()[0]
        p1 = self.new_page(content={'inher':'parent-content'})
        p2 = self.new_page()
        template = django.template.loader.get_template('pages/tests/test7.html')
        context = Context({'current_page': p2, 'lang':'en-us'})
        self.assertEqual(template.render(context), '')
        
        p2.move_to(p1, position='first-child')
        self.assertEqual(template.render(context), 'parent-content')


    def test_placeholder_untranslated_content(self):
        """Test placeholder untranslated content."""
        from pages import settings as pages_settings
        setattr(pages_settings, "PAGE_USE_SITE_ID", False)
        page = self.new_page(content={})
        placeholder = PlaceholderNode('untrans', page='p', untranslated=True)
        placeholder.save(page, 'fr-ch', 'test-content', True)
        placeholder.save(page, 'en-us', 'test-content', True)
        self.assertEqual(len(Content.objects.all()), 1)
        self.assertEqual(Content.objects.all()[0].language, 'en-us')

        placeholder = PlaceholderNode('untrans', page='p', untranslated=False)
        placeholder.save(page, 'fr-ch', 'test-content', True)
        self.assertEqual(len(Content.objects.all()), 2)

        # test the syntax
        page = self.new_page()
        template = django.template.loader.get_template('pages/tests/test8.html')
        context = Context({'current_page': page, 'lang':'en-us'})
        self.assertEqual(template.render(context), '')

    def test_urlconf_registry(self):
        """Test urlconf_registry basic functions."""
        reg.register_urlconf('Documents', 'example.documents.urls',
            label='Display documents')
        
        reg.get_urlconf('Documents')
        try:
            reg.register_urlconf('Documents', 'example.documents.urls',
            label='Display documents')
        except reg.UrlconfAlreadyRegistered:
            pass
        reg.registry = []
        try:
            reg.get_urlconf('Documents')
        except reg.UrlconfNotFound:
            pass
        
        reg.register_urlconf('Documents', 'example.documents.urls',
            label='Display documents')

        self.assertEqual(reg.get_choices(),
            [('', 'No delegation'), ('Documents', 'Display documents')])

    def test_permissions(self):
        """Test the permissions lightly."""
        
        from pages.permissions import PagePermission
        admin = User.objects.get(username='admin')
        page = self.new_page()
        pp = PagePermission(user=page.author)
        self.assertTrue(pp.check('change', page=page, method='GET'))
        self.assertTrue(pp.check('change', page=page, method='POST'))
        
        staff = User.objects.get(username='staff')
        pp = PagePermission(user=staff)
        # weird because nonstaff?
        self.assertTrue(pp.check('change', page=page, method='GET',
            lang='en-us'))
        self.assertFalse(pp.check('change', page=page, method='POST',
            lang='en-us'))
