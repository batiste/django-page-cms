from django.test import TestCase

from pages.models import *
from django.test.client import Client

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
        page_data = {'title':'test page', 'slug':'test-page', 'language':'en', 'sites':[1], 'status':1}
        response = c.post('/admin/pages/page/add/', page_data)
        self.assertRedirects(response, '/admin/pages/page/')
