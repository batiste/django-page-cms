from django.test import TestCase
from pages.models import *
from django.test.client import Client

class PagesTestCase(TestCase):
    fixtures = ['tests.json']

    def test_01_add_page(self):
        """
        Test that the add admin page could be displayed correctly
        """
        c = Client()
        c.login(username= 'batiste', password='b')
        response = c.get('/admin/pages/page/add/')
        assert(response.status_code == 200)
        
