from django.test import TestCase
import settings
from pages.models import *
from django.test.client import Client

page_data = {'title':'test page', 'slug':'test-page', 'language':'en', 'sites':[1], 'status':1}

class PagesTestCase(TestCase):
    fixtures = ['tests.json']


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
        c = Client()
        c.login(username= 'batiste', password='b')
        response = c.post('/admin/pages/page/add/', page_data)
        self.assertRedirects(response, '/admin/pages/page/')
        slug_content = Content.objects.get_page_slug(page_data['slug'])
        assert(slug_content is not None)
        page = slug_content.page
        assert(page.title() == page_data['title'])
        assert(page.slug() == page_data['slug'])

    def test_03_slug_collision(self):
        """
        Test a slug collision
        """
        c = Client()
        c.login(username= 'batiste', password='b')
        response = c.post('/admin/pages/page/add/', page_data)
        self.assertRedirects(response, '/admin/pages/page/')
        page1 = Content.objects.get_page_slug(page_data['slug']).page

        response = c.post('/admin/pages/page/add/', page_data)
        assert(response.status_code == 200)

        settings.PAGE_UNIQUE_SLUG_REQUIRED = False
        response = c.post('/admin/pages/page/add/', page_data)
        self.assertRedirects(response, '/admin/pages/page/')
        page2 = Content.objects.get_page_slug(page_data['slug']).page
        assert(page1.id != page2.id)


