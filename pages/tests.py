# -*- coding: utf-8 -*-
import django
from django.test import TestCase
import settings
from pages.models import *
from django.test.client import Client
from django.template import Template, RequestContext, TemplateDoesNotExist

class PagesTestCase(TestCase):
    fixtures = ['tests.json']
    counter = 1

    def get_new_page_data(self):
        page_data = {'title':'test page %d' % self.counter, 
            'slug':'test-page-%d' % self.counter, 'language':'en-us',
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
        self.assertEqual(response.status_code, 200)


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
        self.assertEqual(page.title(), page_data['title'])
        self.assertEqual(page.slug(), page_data['slug'])

    def test_03_slug_collision(self):
        """
        Test a slug collision
        """
        setattr(settings, "PAGE_UNIQUE_SLUG_REQUIRED", True)

        c = Client()
        c.login(username= 'batiste', password='b')
        page_data = self.get_new_page_data()
        response = c.post('/admin/pages/page/add/', page_data)
        self.assertRedirects(response, '/admin/pages/page/')

        setattr(settings, "PAGE_UNIQUE_SLUG_REQUIRED", False)
        
        response = c.post('/admin/pages/page/add/', page_data)
        self.assertEqual(response.status_code, 200)

        page1 = Content.objects.get_content_slug_by_slug(page_data['slug']).page
        page_data['position'] = 'first-child'
        page_data['target'] = page1.id
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
        self.assertRedirects(response, '/admin/pages/page/')

        response = c.get('/pages/test-page-2/')
        self.assertEqual(response.status_code, 200)

    def test_05_edit_page(self):
        """
        Test that a page can edited via the admin
        """
        c = Client()
        c.login(username= 'batiste', password='b')
        page_data = self.get_new_page_data()
        response = c.post('/admin/pages/page/add/', page_data)
        self.assertRedirects(response, '/admin/pages/page/')
        page = Page.objects.all()[0]
        response = c.get('/admin/pages/page/%d/' % page.id)
        self.assertEqual(response.status_code, 200)
        page_data['title'] = 'changed title'
        page_data['body'] = 'changed body'
        response = c.post('/admin/pages/page/%d/' % page.id, page_data)
        self.assertRedirects(response, '/admin/pages/page/')
        page = Page.objects.get(id=page.id)
        self.assertEqual(page.title(), 'changed title')
        body = Content.objects.get_content(page, 'en-us', 'body')
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
        setattr(settings, "PAGE_DEFAULT_LANGUAGE", 'fr-ch')
        response = c.get('/admin/pages/page/add/')
        self.assertContains(response, 'value="fr-ch" selected="selected"')

        page_data = self.get_new_page_data()
        page_data["title"] = 'english title'
        response = c.post('/admin/pages/page/add/', page_data)
        self.assertRedirects(response, '/admin/pages/page/')

        page = Page.objects.all()[0]

        # this test only works in version superior of 1.0.2
        django_version =  django.get_version().rsplit()[0].split('.')
        if len(django_version) > 2:
            major, middle, minor = [int(v) for v in django_version]
        else:
            major, middle = [int(v) for v in django_version]
        if major >=1 and middle > 0:
            response = c.get('/admin/pages/page/%d/?language=de' % page.id)
            self.assertContains(response, 'value="de" selected="selected"')

        # add a french version of the same page
        page_data["language"] = 'fr-ch'
        page_data["title"] = 'french title'
        response = c.post('/admin/pages/page/%d/' % page.id, page_data)
        self.assertRedirects(response, '/admin/pages/page/')

        setattr(settings, "PAGE_DEFAULT_LANGUAGE", 'en-us')
        
        # test that the frontend view use the good parameters
        # I cannot find a way of setting the accept-language HTTP 
        # header so I used django_language cookie instead
        c = Client()
        c.cookies["django_language"] = 'en-us'
        response = c.get('/pages/')
        self.assertContains(response, 'english title')
        self.assertContains(response, 'lang="en-us"')
        self.assertNotContains(response, 'french title')
        
        c = Client()
        c.cookies["django_language"] = 'fr-ch'
        response = c.get('/pages/')
        self.assertContains(response, 'french title')
        self.assertContains(response, 'lang="fr-ch"')
        
        self.assertNotContains(response, 'english title')

        # this should be mapped to the fr-ch content
        c = Client()
        c.cookies["django_language"] = 'fr-fr'
        response = c.get('/pages/')
        self.assertContains(response, 'french title')
        self.assertContains(response, 'lang="fr-ch"')

        
    def test_08_revision(self):
        """
        Test that a page can edited several times
        """
        c = Client()
        c.login(username= 'batiste', password='b')
        page_data = self.get_new_page_data()
        response = c.post('/admin/pages/page/add/', page_data)
        page = Page.objects.all()[0]
        
        page_data['body'] = 'changed body'
        response = c.post('/admin/pages/page/%d/' % page.id, page_data)
        self.assertEqual(Content.objects.get_content(page, 'en-us', 'body'), 'changed body')

        page_data['body'] = 'changed body 2'
        response = c.post('/admin/pages/page/%d/' % page.id, page_data)
        self.assertEqual(Content.objects.get_content(page, 'en-us', 'body'), 'changed body 2')

        response = c.get('/pages/')
        self.assertContains(response, 'changed body 2', 1)
        
        setattr(settings, "PAGE_CONTENT_REVISION", False)
        
        self.assertEqual(Content.objects.get_content(page, 'en-us', 'body'), 'changed body 2')

    def test_09_placeholder(self):
        """
        Test that the placeholder is correctly displayed in
        the admin
        """
        setattr(settings, "SITE_ID", 2)
        c = Client()
        c.login(username= 'batiste', password='b')
        page_data = self.get_new_page_data()
        page_data['template'] = 'pages/nice.html'
        response = c.post('/admin/pages/page/add/', page_data)
        page = Page.objects.all()[0]
        response = c.get('/admin/pages/page/%d/' % page.id)
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, 'name="right-column"', 1)

    def test_10_directory_slug(self):
        """
        Test diretory slugs
        """
        setattr(settings, "PAGE_UNIQUE_SLUG_REQUIRED", False)
        c = Client()
        c.login(username= 'batiste', password='b')

        page_data = self.get_new_page_data()
        page_data['title'] = 'parent title'
        page_data['slug'] = 'same-slug'
        response = c.post('/admin/pages/page/add/', page_data)
        # the redirect tell that the page has been create correctly
        self.assertRedirects(response, '/admin/pages/page/')

        page = Page.objects.all()[0]

        response = c.post('/admin/pages/page/add/', page_data)
        # we cannot create 2 root page with the same slug
        # this assert test that the creation fails as wanted
        self.assertEqual(response.status_code, 200)

        response = c.get('/pages/same-slug/')

        page1 = Content.objects.get_content_slug_by_slug(page_data['slug']).page
        self.assertEqual(page1.id, page.id)

        page_data['title'] = 'children title'
        page_data['target'] = page1.id
        page_data['position'] = 'first-child'
        response = c.post('/admin/pages/page/add/', page_data)
        self.assertRedirects(response, '/admin/pages/page/')

        # finaly test that we can get every page according the path
        response = c.get('/pages/same-slug/')
        self.assertContains(response, "parent title", 2)

        response = c.get('/pages/same-slug/same-slug/')
        self.assertContains(response, "children title", 2)

    def test_11_show_content_tag(self):
        """
        Test the {% show_content %} template tag
        """
        c = Client()
        c.login(username= 'batiste', password='b')
        page_data = self.get_new_page_data()
        response = c.post('/admin/pages/page/add/', page_data)
        page = Page.objects.all()[0]
        class request:
            REQUEST = {'language': 'en'}
            GET = {}
        context = RequestContext(request, {'page': page})
        template = Template('{% load pages_tags %}'
                            '{% show_content page "title" "en-us" %}')
        self.assertEqual(template.render(context), page_data['title'] + '\n')
        template = Template('{% load pages_tags %}'
                            '{% show_content page "title" %}')
        self.assertEqual(template.render(context), page_data['title'] + '\n')

    def test_12_get_content_tag(self):
        """
        Test the {% get_content %} template tag
        """
        c = Client()
        c.login(username= 'batiste', password='b')
        page_data = self.get_new_page_data()
        response = c.post('/admin/pages/page/add/', page_data)
        page = Page.objects.all()[0]
        class request:
            REQUEST = {'language': 'en'}
            GET = {}
        context = RequestContext(request, {'page': page})
        template = Template('{% load pages_tags %}'
                            '{% get_content page "title" "en-us" as content %}'
                            '{{ content }}')
        self.assertEqual(template.render(context), page_data['title'])
        template = Template('{% load pages_tags %}'
                            '{% get_content page "title" as content %}'
                            '{{ content }}')
        self.assertEqual(template.render(context), page_data['title'])