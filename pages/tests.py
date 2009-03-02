# -*- coding: utf-8 -*-
import django
from django.test import TestCase
import settings
from pages.models import *
from django.test.client import Client
from django.template import TemplateDoesNotExist

class PagesTestCase(TestCase):
    fixtures = ['tests.json']
    counter = 1

    def get_new_page_data(self):
        page_data = {'title':'test page %d' % self.counter, 
            'slug':'test-page-%d' % self.counter, 'language':'en',
            'sites':[2], 'status':Page.PUBLISHED}
        self.counter = self.counter + 1
        return page_data

    def test_01_add_page(self):
        """
        Test that the add admin page could be displayed via the admin
        """
        c = Client()
        c.login(username= 'batiste', password='b')
        response = c.get('/admin/pages/page/add/')
        assert(response.status_code == 200)


    def test_02_create_page(self):
        """
        Test that a page can be created via the admin
        """
        setattr(settings, "SITE_ID", 2)
        c = Client()
        c.login(username= 'batiste', password='b')
        page_data = self.get_new_page_data()
        response = c.post('/admin/pages/page/add/', page_data)
        self.assertRedirects(response, '/admin/pages/page/')
        slug_content = Content.objects.get_content_slug_by_slug(page_data['slug'])
        assert(slug_content is not None)
        page = slug_content.page
        assert(page.title() == page_data['title'])
        assert(page.slug() == page_data['slug'])

    def test_03_slug_collision(self):
        """
        Test a slug collision
        """
        setattr(settings, "SITE_ID", 2)
        
        c = Client()
        c.login(username= 'batiste', password='b')
        page_data = self.get_new_page_data()
        response = c.post('/admin/pages/page/add/', page_data)
        self.assertRedirects(response, '/admin/pages/page/')
        
        page1 = Content.objects.get_content_slug_by_slug(page_data['slug']).page

        response = c.post('/admin/pages/page/add/', page_data)
        self.assertEqual(response.status_code, 200)

        settings.PAGE_UNIQUE_SLUG_REQUIRED = False
        response = c.post('/admin/pages/page/add/', page_data)
        self.assertRedirects(response, '/admin/pages/page/')
        page2 = Content.objects.get_content_slug_by_slug(page_data['slug']).page
        self.assertNotEqual(page1.id, page2.id)

    def test_04_details_view(self):
        """
        Test the details view
        """

        c = Client()
        c.login(username= 'batiste', password='b')
        try:
            response = c.get('/pages/')
        except TemplateDoesNotExist, e:
            if e.args != ('404.html',):
                raise

        page_data = self.get_new_page_data()
        page_data['status'] = Page.DRAFT
        response = c.post('/admin/pages/page/add/', page_data)
        try:
            response = c.get('/pages/')
        except TemplateDoesNotExist, e:
            if e.args != ('404.html',):
                raise

        page_data = self.get_new_page_data()
        page_data['status'] = Page.PUBLISHED
        page_data['slug'] = 'test-page-2'
        response = c.post('/admin/pages/page/add/', page_data)
        response = c.get('/admin/pages/page/')
        
        response = c.get('/pages/')
        self.assertEqual(response.status_code, 200)

    def test_05_edit_page(self):
        """
        Test that a page can edited via the admin
        """
        c = Client()
        c.login(username= 'batiste', password='b')
        page_data = self.get_new_page_data()
        response = c.post('/admin/pages/page/add/', page_data)
        response = c.get('/admin/pages/page/1/')
        self.assertEqual(response.status_code, 200)
        page_data['title'] = 'changed title'
        page_data['body'] = 'changed body'
        response = c.post('/admin/pages/page/1/', page_data)
        self.assertRedirects(response, '/admin/pages/page/')
        page = Page.objects.get(id=1)
        self.assertEqual(page.title(), 'changed title')
        body = Content.objects.get_content(page, 'en', 'body')
        self.assertEqual(body, 'changed body')
        
    def test_06_site_framework(self):
        """
        Test the site framework, and test if it's possible to disable it
        """
        setattr(settings, "SITE_ID", 2)
        setattr(settings, "PAGE_USE_SITE_ID", True)
        
        c = Client()
        c.login(username= 'batiste', password='b')
        page_data = self.get_new_page_data()
        page_data["sites"] = [2]
        response = c.post('/admin/pages/page/add/', page_data)
        self.assertRedirects(response, '/admin/pages/page/')
        
        page = Content.objects.get_content_slug_by_slug(page_data['slug']).page
        self.assertEqual(page.sites.count(), 1)
        self.assertEqual(page.sites.all()[0].id, 2)
        
        page_data = self.get_new_page_data()
        page_data["sites"] = [3]
        response = c.post('/admin/pages/page/add/', page_data)
        self.assertRedirects(response, '/admin/pages/page/')

        # we cannot get a slug that doesn't exist
        content = Content.objects.get_content_slug_by_slug("this doesn't exist")
        
        # we cannot get the data posted on another site
        content = Content.objects.get_content_slug_by_slug(page_data['slug'])
        self.assertEqual(content, None)
        
        setattr(settings, "SITE_ID", 3)
        page = Content.objects.get_content_slug_by_slug(page_data['slug']).page
        self.assertEqual(page.sites.count(), 1)
        self.assertEqual(page.sites.all()[0].id, 3)
        
        # with param
        self.assertEqual(Page.objects.on_site(2).count(), 1)
        self.assertEqual(Page.objects.on_site(3).count(), 1)
        
        # without param
        self.assertEqual(Page.objects.on_site().count(), 1)
        setattr(settings, "SITE_ID", 2)
        self.assertEqual(Page.objects.on_site().count(), 1)
        
        page_data = self.get_new_page_data()
        page_data["sites"] = [2, 3]
        response = c.post('/admin/pages/page/add/', page_data)
        self.assertRedirects(response, '/admin/pages/page/')
        
        self.assertEqual(Page.objects.on_site(3).count(), 2)
        self.assertEqual(Page.objects.on_site(2).count(), 2)
        self.assertEqual(Page.objects.on_site().count(), 2)
        
        setattr(settings, "PAGE_USE_SITE_ID", False)
        
        # we should get everything
        self.assertEqual(Page.objects.on_site().count(), 3)

    def test_07_languages(self):
        """
        Test post a page with different languages
        and test that the default view works correctly
        """
        c = Client()
        user = c.login(username= 'batiste', password='b')
        
        # test that the default language setting is used add page admin
        # and not accept-language in HTTP requests.
        setattr(settings, "PAGE_DEFAULT_LANGUAGE", 'de')
        response = c.get('/admin/pages/page/add/')
        self.assertContains(response, 'value="de" selected="selected"')
        setattr(settings, "PAGE_DEFAULT_LANGUAGE", 'fr')
        response = c.get('/admin/pages/page/add/')
        self.assertContains(response, 'value="fr" selected="selected"')

        page_data = self.get_new_page_data()
        page_data["title"] = 'english title'
        response = c.post('/admin/pages/page/add/', page_data)
        self.assertRedirects(response, '/admin/pages/page/')

        # this test only works in version superior of 1.0.2
        major, middle, minor = [int(v) for v in django.get_version().rsplit()[0].split('.')]
        if major >=1 and middle > 0:
            response = c.get('/admin/pages/page/1/?language=de')
            self.assertContains(response, 'value="de" selected="selected"')
        
        page_data["language"] = 'fr'
        page_data["title"] = 'french title'
        response = c.post('/admin/pages/page/1/', page_data)
        self.assertRedirects(response, '/admin/pages/page/')
        
        # test that the frontend view use the good parameters
        # I cannot find a way of setting the accept-language HTTP 
        # header so I used django_language cookie instead
        c = Client()
        c.cookies["django_language"] = 'en'
        response = c.get('/pages/')
        self.assertContains(response, 'english title')
        self.assertNotContains(response, 'french title')
        
        c = Client()
        c.cookies["django_language"] = 'fr'
        response = c.get('/pages/')
        self.assertContains(response, 'french title')
        self.assertContains(response, 'lang="fr"')
        self.assertNotContains(response, 'english title')
        
        

