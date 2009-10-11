# -*- coding: utf-8 -*-
"""Django page CMS test suite module"""
import django
from django.conf import settings
from django.test.client import Client
from django.template import Template, RequestContext, TemplateDoesNotExist
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response

from pages.models import Page, Content, PageAlias
from pages.tests.testcase import TestCase

class PagesTestCase(TestCase):
    """Django page CMS test suite class"""
    
    def test_01_add_page(self):
        """Test that the add admin page could be displayed via the
        admin"""
        c = Client()
        c.login(username= 'batiste', password='b')
        response = c.get('/admin/pages/page/add/')
        self.assertEqual(response.status_code, 200)


    def test_02_create_page(self):
        """Test that a page can be created via the admin."""
        #setattr(settings, "SITE_ID", 2)
        c = Client()
        c.login(username= 'batiste', password='b')
        page_data = self.get_new_page_data()
        response = c.post('/admin/pages/page/add/', page_data)
        self.assertRedirects(response, '/admin/pages/page/')
        slug_content = Content.objects.get_content_slug_by_slug(
            page_data['slug']
        )
        assert(slug_content is not None)
        page = slug_content.page
        self.assertEqual(page.title(), page_data['title'])
        self.assertEqual(page.slug(), page_data['slug'])
        self.assertNotEqual(page.last_modification_date, None)

    def test_03_slug_collision(self):
        """Test a slug collision."""
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
        """Test the details view"""

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
        page_data['template'] = 'pages/index.html'
        response = c.post('/admin/pages/page/add/', page_data)
        self.assertRedirects(response, '/admin/pages/page/')

        response = c.get('/pages/test-page-2/')
        self.assertEqual(response.status_code, 200)

    def test_05_edit_page(self):
        """Test that a page can edited via the admin"""
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
        """Test the site framework, and test if it's possible to
        disable it"""

        # this is necessary to make the test pass
        from pages import settings as pages_settings
        setattr(pages_settings, "SITE_ID", 2)
        setattr(pages_settings, "PAGE_USE_SITE_ID", True)

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
        self.assertEqual(content, None)

        # we cannot get the data posted on another site
        content = Content.objects.get_content_slug_by_slug(page_data['slug'])
        self.assertEqual(content, None)

        setattr(pages_settings, "SITE_ID", 3)
        page = Content.objects.get_content_slug_by_slug(page_data['slug']).page
        self.assertEqual(page.sites.count(), 1)
        self.assertEqual(page.sites.all()[0].id, 3)

        # with param
        self.assertEqual(Page.objects.on_site(2).count(), 1)
        self.assertEqual(Page.objects.on_site(3).count(), 1)

        # without param
        self.assertEqual(Page.objects.on_site().count(), 1)
        setattr(pages_settings, "SITE_ID", 2)
        self.assertEqual(Page.objects.on_site().count(), 1)

        page_data = self.get_new_page_data()
        page_data["sites"] = [2, 3]
        response = c.post('/admin/pages/page/add/', page_data)
        self.assertRedirects(response, '/admin/pages/page/')

        self.assertEqual(Page.objects.on_site(3).count(), 2)
        self.assertEqual(Page.objects.on_site(2).count(), 2)
        self.assertEqual(Page.objects.on_site().count(), 2)

        setattr(pages_settings, "PAGE_USE_SITE_ID", False)

        # we should get everything
        self.assertEqual(Page.objects.on_site().count(), 3)

    def test_07_languages(self):
        """Test post a page with different languages
        and test that the admin views works correctly."""
        c = Client()
        user = c.login(username= 'batiste', password='b')
        
        # test that the client language setting is used in add page admin
        c.cookies["django_language"] = 'de'
        response = c.get('/admin/pages/page/add/')
        self.assertContains(response, 'value="de" selected="selected"')
        c.cookies["django_language"] = 'fr-ch'
        response = c.get('/admin/pages/page/add/')
        self.assertContains(response, 'value="fr-ch" selected="selected"')

        page_data = self.get_new_page_data()
        page_data["title"] = 'english title'
        response = c.post('/admin/pages/page/add/', page_data)
        self.assertRedirects(response, '/admin/pages/page/')

        page = Page.objects.all()[0]
        self.assertEqual(page.get_languages(), ['en-us'])

        # this test only works in version superior of 1.0.2
        django_version =  django.get_version().rsplit()[0].split('.')
        if len(django_version) > 2:
            major, middle, minor = [int(v) for v in django_version]
        else:
            major, middle = [int(v) for v in django_version]
        if major >= 1 and middle > 0:
            response = c.get('/admin/pages/page/%d/?language=de' % page.id)
            self.assertContains(response, 'value="de" selected="selected"')

        # add a french version of the same page
        page_data["language"] = 'fr-ch'
        page_data["title"] = 'french title'
        response = c.post('/admin/pages/page/%d/' % page.id, page_data)
        self.assertRedirects(response, '/admin/pages/page/')

        #setattr(settings, "PAGE_DEFAULT_LANGUAGE", 'en-us')
        
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
        """Test that a page can edited several times."""
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
        response = c.get('/pages/same-slug/')
        self.assertEqual(response.status_code, 200)

        page = Page.objects.all()[0]

        response = c.post('/admin/pages/page/add/', page_data)
        # we cannot create 2 root page with the same slug
        # this assert test that the creation fails as wanted
        self.assertEqual(response.status_code, 200)

        page1 = Content.objects.get_content_slug_by_slug(page_data['slug']).page
        self.assertEqual(page1.id, page.id)

        page_data['title'] = 'children title'
        page_data['target'] = page1.id
        page_data['position'] = 'first-child'
        response = c.post('/admin/pages/page/add/', page_data)
        self.assertRedirects(response, '/admin/pages/page/')

        # finaly test that we can get every page according the path
        response = c.get('/pages/same-slug')
        self.assertContains(response, "parent title", 2)

        response = c.get('/pages/same-slug/same-slug')
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
        context = RequestContext(request, {'page': page, 'lang':'en-us',
            'path':'/page-1/'})
        template = Template('{% load pages_tags %}'
                            '{% show_content page "title" "en-us" %}')
        self.assertEqual(template.render(context), page_data['title'])
        template = Template('{% load pages_tags %}'
                            '{% show_content page "title" %}')
        self.assertEqual(template.render(context), page_data['title'])

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


    def test_17_request_mockup(self):
        from pages.utils import get_request_mock
        request = get_request_mock()
        self.assertEqual(hasattr(request, 'session'), True)

    def test_18_tree_admin_interface(self):
        """
        Test that moving/creating page in the tree is working properly
        using the admin interface
        """
        c = Client()
        c.login(username= 'batiste', password='b')
        page_data = self.get_new_page_data()
        page_data['slug'] = 'root'

        response = c.post('/admin/pages/page/add/', page_data)
        
        root_page = Content.objects.get_content_slug_by_slug('root').page
        self.assertTrue(root_page.is_first_root())
        page_data['position'] = 'first-child'
        page_data['target'] = root_page.id
        page_data['slug'] = 'child-1'
        response = c.post('/admin/pages/page/add/', page_data)
        
        child_1 = Content.objects.get_content_slug_by_slug('child-1').page
        self.assertFalse(child_1.is_first_root())
        
        page_data['slug'] = 'child-2'
        response = c.post('/admin/pages/page/add/', page_data)

        child_2 = Content.objects.get_content_slug_by_slug('child-2').page

        self.assertEqual(str(Page.objects.all()),
            "[<Page: root>, <Page: child-2>, <Page: child-1>]")
        # move page 1 in the first position
        response = c.post('/admin/pages/page/%d/move-page/' % child_1.id,
            {'position':'first-child', 'target':root_page.id})

        self.assertEqual(str(Page.objects.all()),
            "[<Page: root>, <Page: child-1>, <Page: child-2>]")

        # move page 2 in the first position
        response = c.post('/admin/pages/page/%d/move-page/' % child_2.id,
            {'position': 'left', 'target': child_1.id})
        
        self.assertEqual(str(Page.objects.all()),
            "[<Page: root>, <Page: child-2>, <Page: child-1>]")

        # try to create a sibling with the same slug, via left, right
        from pages import settings as pages_settings
        setattr(pages_settings, "PAGE_UNIQUE_SLUG_REQUIRED", False)
        page_data['target'] = child_2.id
        page_data['position'] = 'left'
        response = c.post('/admin/pages/page/add/', page_data)
        self.assertEqual(response.status_code, 200)

        # try to create a sibling with the same slug, via first-child
        page_data['target'] = root_page.id
        page_data['position'] = 'first-child'
        response = c.post('/admin/pages/page/add/', page_data)
        self.assertEqual(response.status_code, 200)
        # try to create a second page 2 in root
        del page_data['target']
        del page_data['position']

        setattr(pages_settings, "PAGE_UNIQUE_SLUG_REQUIRED", True)
        # cannot create because slug exists
        response = c.post('/admin/pages/page/add/', page_data)
        self.assertEqual(response.status_code, 200)
        # Now it should work beause the page is not a sibling
        setattr(pages_settings, "PAGE_UNIQUE_SLUG_REQUIRED", False)
        response = c.post('/admin/pages/page/add/', page_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Page.objects.count(), 4)
        # Should not work because we already have sibling at the same level
        response = c.post('/admin/pages/page/add/', page_data)
        self.assertEqual(response.status_code, 200)

        # try to change the page 2 slug into page 1
        page_data['slug'] = 'child-1'
        response = c.post('/admin/pages/page/%d/' % child_2.id, page_data)
        self.assertEqual(response.status_code, 200)
        setattr(pages_settings, "PAGE_UNIQUE_SLUG_REQUIRED", True)
        response = c.post('/admin/pages/page/%d/' % child_2.id, page_data)
        self.assertEqual(response.status_code, 200)

    def test_19_tree(self):
        """
        Test that the navigation tree works properly with mptt
        """
        c = Client()
        c.login(username= 'batiste', password='b')
        page_data = self.get_new_page_data()
        page_data['slug'] = 'page1'
        response = c.post('/admin/pages/page/add/', page_data)
        page_data['slug'] = 'page2'
        response = c.post('/admin/pages/page/add/', page_data)
        page_data['slug'] = 'page3'
        response = c.post('/admin/pages/page/add/', page_data)
        self.assertEqual(str(Page.objects.navigation()),
            "[<Page: page1>, <Page: page2>, <Page: page3>]")

        p1 = Content.objects.get_content_slug_by_slug('page1').page
        p2 = Content.objects.get_content_slug_by_slug('page2').page
        p3 = Content.objects.get_content_slug_by_slug('page3').page
        
        p2.move_to(p1, 'left')
        p2.save()

        self.assertEqual(str(Page.objects.navigation()),
            "[<Page: page2>, <Page: page1>, <Page: page3>]")

        p3.move_to(p2, 'left')
        p3.save()

        self.assertEqual(str(Page.objects.navigation()),
            "[<Page: page3>, <Page: page2>, <Page: page1>]")

        p1 = Content.objects.get_content_slug_by_slug('page1').page
        p2 = Content.objects.get_content_slug_by_slug('page2').page
        p3 = Content.objects.get_content_slug_by_slug('page3').page

        p3.move_to(p1, 'first-child')
        p2.move_to(p1, 'first-child')

        self.assertEqual(str(Page.objects.navigation()),
            "[<Page: page1>]")

        p3 = Content.objects.get_content_slug_by_slug('page3').page
        p3.move_to(p1, 'left')
        
        self.assertEqual(str(Page.objects.navigation()),
            "[<Page: page3>, <Page: page1>]")
            
    
    def test_20_ajax_language(self):
        """Test that language is working properly"""
        c = Client()
        c.login(username= 'batiste', password='b')
        # Activate a language other than settings.LANGUAGE_CODE
        response = c.post('/i18n/setlang/', {'language':'fr-ch' })
        self.assertEqual(c.session.get('django_language', False), 'fr-ch')
        
        # Make sure we're in french
        response = c.get('/admin/pages/page/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Auteur' in response.content)
        
        # Create some pages (taken from test_18_tree_admin_interface)
        page_data = self.get_new_page_data()
        page_data['slug'] = 'root'
        response = c.post('/admin/pages/page/add/', page_data)
        
        root_page = Content.objects.get_content_slug_by_slug('root').page
        page_data['position'] = 'first-child'
        page_data['target'] = root_page.id
        page_data['slug'] = 'child-1'
        response = c.post('/admin/pages/page/add/', page_data)
        
        child_1 = Content.objects.get_content_slug_by_slug('child-1').page
        
        page_data['slug'] = 'child-2'
        response = c.post('/admin/pages/page/add/', page_data)

        child_2 = Content.objects.get_content_slug_by_slug('child-2').page

        self.assertEqual(str(Page.objects.all()),
            "[<Page: root>, <Page: child-2>, <Page: child-1>]")
            
        """
        The relevant bit, fixed by rev 501: the response issued by a move
        command returns content localized in settings.LANGUAGE_CODE (i.e. 'en´)
        even though the original AJAX request passed in a the correct 
        session ID localizing this client as fr-ch
        
        This is probably because the LocaleMiddleware gets instantiated
        with a couple request_mocks which have no real connection to the 
        AJAX request *but* django.utils.translation caches the active
        language on a per thread basis.
        
        This means that the first "bogus" call to LocaleMiddleware.process_request
        will "kill" the localization data for the AJAX request.
        
        Rev. 501 fixes this by passing in the language code from the original request.
        
        """
        response = c.post('/admin/pages/page/%d/move-page/' % child_1.id,
            {'position':'first-child', 'target':root_page.id})
            
        # Make sure the content response we got was in french
        self.assertTrue('Auteur' in response.content)

    def test_21_view_context(self):
        """
        Test that the default view can only return the context
        """
        
        c = Client()
        c.login(username= 'batiste', password='b')
        page_data = self.get_new_page_data()
        page_data['slug'] = 'page1'
        # create a page for the example otherwise you will get a Http404 error
        response = c.post('/admin/pages/page/add/', page_data)
        page1 = Content.objects.get_content_slug_by_slug('page1').page

        from pages.views import details
        from pages.utils import get_request_mock
        request = get_request_mock()
        context = details(request, only_context=True)
        self.assertEqual(context['current_page'], page1)

    def test_24_page_valid_targets(self):
        """Test page valid_targets method"""
        c = Client()
        c.login(username= 'batiste', password='b')
        page_data = self.get_new_page_data()
        page_data['slug'] = 'root'
        response = c.post('/admin/pages/page/add/', page_data)
        root_page = Content.objects.get_content_slug_by_slug('root').page
        page_data['position'] = 'first-child'
        page_data['target'] = root_page.id
        page_data['slug'] = 'child-1'
        response = c.post('/admin/pages/page/add/', page_data)
        self.assertEqual(response.status_code, 302)
        c1 = Content.objects.get_content_slug_by_slug('child-1').page

        root_page = Content.objects.get_content_slug_by_slug('root').page
        self.assertEqual(len(root_page.valid_targets()), 0)
        self.assertEqual(str(c1.valid_targets()),
                                            "[<Page: root>]")

    def test_25_page_admin_view(self):
        """Test page admin view"""
        c = Client()
        c.login(username= 'batiste', password='b')
        page_data = self.get_new_page_data()
        page_data['slug'] = 'page-1'
        response = c.post('/admin/pages/page/add/', page_data)
        page = Content.objects.get_content_slug_by_slug('page-1').page
        self.assertEqual(page.status, 1)
        response = c.post('/admin/pages/page/%d/change-status/' %
            page.id, {'status':Page.DRAFT})
        page = Content.objects.get_content_slug_by_slug('page-1').page
        self.assertEqual(page.status, Page.DRAFT)

        url = '/admin/pages/page/%d/modify-content/title/en-us/' % page.id
        response = c.post(url, {'content': 'test content'})
        self.assertEqual(page.title(), 'test content')

        # TODO: realy test these methods
        url = '/admin/pages/page/%d/traduction/en-us/' % page.id
        response = c.get(url)
        self.assertEqual(response.status_code, 200)
        
        url = '/admin/pages/page/%d/sub-menu/' % page.id
        response = c.get(url)
        self.assertEqual(response.status_code, 200)

        url = '/admin/pages/page/%d/get-content/1/' % page.id
        response = c.get(url)
        self.assertEqual(response.status_code, 200)
        
    def test_26_page_alias(self):
        """Test page aliasing system"""

        c = Client()
        c.login(username= 'batiste', password='b')
        
        # create some pages
        page_data = self.get_new_page_data()
        page_data['title'] = 'home-page-title'
        page_data['slug'] = 'home-page'
        response = c.post('/admin/pages/page/add/', page_data)
        self.assertRedirects(response, '/admin/pages/page/')
        
        page_data['title'] =  'downloads-page-title'
        page_data['slug'] = 'downloads-page'
        response = c.post('/admin/pages/page/add/', page_data)
        self.assertRedirects(response, '/admin/pages/page/')
        
        # create aliases for the pages
        page = Page.objects.from_path('home-page', None)
        self.assertTrue(page)
        p = PageAlias(page=page, url='/index.php')
        p.save()
        
        page = Page.objects.from_path('downloads-page', None)
        self.assertTrue(page)
        p = PageAlias(page=page, url='index.php?page=downloads')
        p.save()
        
        # now check whether we can retrieve the pages.
        # is the homepage available from is alias
        response = c.get('/pages/index.php')
        self.assertRedirects(response, '/pages/home-page', 301)

        # for the download page, the slug is canonical
        response = c.get('/pages/downloads-page/')
        self.assertContains(response, "downloads-page-title", 2)
        
        # calling via its alias must cause redirect
        response = c.get('/pages/index.php?page=downloads')
        self.assertRedirects(response, '/pages/downloads-page', 301)
       
    def test_27_page_redirect_to(self):
        """Test page redirected to an other page."""

        client = Client()
        client.login(username= 'batiste', password='b')

        # create some pages
        page1 = self.create_new_page(client)
        page2 = self.create_new_page(client)
        
        page1.redirect_to = page2
        page1.save()

        # now check whether you go to the target page.
        response = client.get(page1.get_absolute_url())
        self.assertRedirects(response, page2.get_absolute_url(), 301)

    def test_28_page_redirect_to_url(self):
        """Test page redirected to external url."""

        client = Client()
        client.login(username= 'batiste', password='b')
        page1 = self.create_new_page(client)
        url = 'http://code.google.com/p/django-page-cms/'
        page1.redirect_to_url = url
        page1.save()

        # now check whether we can retrieve the page.
        response = client.get(page1.get_absolute_url())
        self.assertTrue(response.status_code == 301)
        self.assertTrue(response['Location'] == url)
