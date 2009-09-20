from django.test import TestCase
from pages.models import Page, Content, PageAlias
from django.test.client import Client

class TestCase(TestCase):
    """Django page CMS test suite class"""
    fixtures = ['tests.json']
    counter = 1

    def get_new_page_data(self):
        """Helper method for creating page datas"""
        page_data = {'title':'test page %d' % self.counter,
            'slug':'test-page-%d' % self.counter, 'language':'en-us',
            'sites':[2], 'status':Page.PUBLISHED,
            # used to disable an error with connected models
            'document_set-TOTAL_FORMS':0, 'document_set-INITIAL_FORMS':0,
            }
        self.counter = self.counter + 1
        return page_data

    def create_new_page(self, client=None):
        if not client:
            client = Client()
            client.login(username= 'batiste', password='b')
        page_data = self.get_new_page_data()
        response = client.post('/admin/pages/page/add/', page_data)
        self.assertRedirects(response, '/admin/pages/page/')
        slug_content = Content.objects.get_content_slug_by_slug(
            page_data['slug'])
        return slug_content.page