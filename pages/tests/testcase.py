from django.test import TestCase
from pages.cache import cache
from pages.models import Page, Content
from pages.plugins.category.models import Category
from pages import settings as pages_settings
from pages.testproj import test_settings
from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.template import TemplateDoesNotExist
from django.contrib.sites.models import Site
from django.utils.importlib import import_module
from django.core.urlresolvers import clear_url_caches


class MockRequest:
    REQUEST = {'language': 'en'}
    GET = {}
    META = {}


class Error404Expected(Exception):
    """
    A 404 error was expected."
    """
    pass


class TestCase(TestCase):
    """Django page CMS test suite class"""
    fixtures = ['pages_tests.json']
    counter = 1
    settings_to_reset = {}
    old_url_conf = None

    def setUp(self):
        # useful to make sure the tests will be properly
        # executed in an exotic project.
        self.set_setting('PAGE_TEMPLATES',
            test_settings.PAGE_TEMPLATES)
        self.set_setting('PAGE_DEFAULT_TEMPLATE',
            test_settings.PAGE_DEFAULT_TEMPLATE)

        self.old_url_conf = getattr(settings, 'ROOT_URLCONF')
        setattr(settings, 'ROOT_URLCONF', 'pages.testproj.urls')
        clear_url_caches()
        cache.clear()

    def tearDown(self):
        setattr(settings, 'ROOT_URLCONF', self.old_url_conf)
        for name, value in self.settings_to_reset.items():
            setattr(pages_settings, name, value)
        self.reset_urlconf()
        self.settings_to_reset = {}


    def set_setting(self, name, value):
        old_value = getattr(pages_settings, name)
        setattr(pages_settings, name, value)
        if name == 'PAGE_USE_LANGUAGE_PREFIX':
            self.reset_urlconf()
        if name not in self.settings_to_reset:
            self.settings_to_reset[name] = old_value


    def assert404(self, func):
        try:
            response = func()
            if response.status_code != 404:
                raise Error404Expected
        except TemplateDoesNotExist:
            pass

    def get_admin_client(self):
        from django.test.client import Client
        client = Client()
        client.login(username='admin', password='b')
        return client


    def get_page_url(self, path=''):
        return reverse('pages-details-by-path', args=[path])


    def reset_urlconf(self):
        url_conf = getattr(settings, 'ROOT_URLCONF', False)
        if url_conf:
            reload(import_module(url_conf))
        reload(import_module('pages.urls'))
        reload(import_module('pages.testproj.urls'))
        clear_url_caches()


    def get_new_page_data(self, draft=False):
        """Helper method for creating page datas"""
        page_data = {'title': 'test page %d' % self.counter,
            'slug': 'test-page-%d' % self.counter, 'language':'en-us',
            'sites': [1], 'status': Page.DRAFT if draft else Page.PUBLISHED,
            # used to disable an error with connected models
            'document_set-TOTAL_FORMS': 0, 'document_set-INITIAL_FORMS': 0,
            }
        self.counter = self.counter + 1
        return page_data


    def new_page(self, content={'title': 'test-page'}, language='en-us'):
        author = User.objects.all()[0]
        page = Page.objects.create(author=author, status=Page.PUBLISHED,
            template='pages/examples/index.html')
        if pages_settings.PAGE_USE_SITE_ID:
            page.sites.add(Site.objects.get(id=1))
        # necessary to clear old URL cache
        page.invalidate()
        for key, value in content.items():
            Content(page=page, language='en-us', type=key, body=value).save()
        return page


    def create_new_page(self, client=None, draft=False):
        if not client:
            client = self.get_admin_client()
        page_data = self.get_new_page_data(draft=draft)
        response = client.post('/admin/pages/page/add/', page_data)
        self.assertRedirects(response, '/admin/pages/page/')
        slug_content = Content.objects.get_content_slug_by_slug(
            page_data['slug'])
        return slug_content.page

    def get_new_category_data(self):
        """Helper method for creating category datas"""
        category_data = {'title': 'test category %d' % self.counter,
            'slug': 'test-category-%d' % self.counter, 'language':'en-us',
            }
        self.counter = self.counter + 1
        return category_data

    def new_category(self, data=None, language='en-us'):
        if data is None:
            data = {'title': 'Test category', 'slug': 'test-category'}
        data['language'] = language
        return Category.objects.create(**data)

