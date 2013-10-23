# -*- coding: utf-8 -*-
"""Django page category plugin test suite module."""
from django.template.loader import get_template_from_string
from django.template import Template, RequestContext, Context

from models import Category
from pages.tests.testcase import TestCase
from pages.models import Content, Page


import datetime

class CategoryTestCase(TestCase):
    """Category test suite class."""

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
  
    def test_get_pages_for_category_template_tag(self):
        category = self.new_category()
        content = {
            'title': 'test-page',
            'category': category.slug,
        }
        pages = [self.new_page(content=content) for i in xrange(3)]
        tpl = """{% load pages_tags category_tags %}{% pages_for_category 'test-category' %}{% for page in pages %}{{ page.title }}
        {% endfor %}"""
        template = get_template_from_string(tpl)
        out = template.render(Context({}))
        easy_out = out.strip().replace('\n', '').replace(8 * ' ', ' ')
        self.assertEqual(easy_out, 'test-page test-page test-page')

    def test_get_category_name(self):
        tpl = """{% load pages_tags category_tags %}{% category_name 'test-category' %}"""
        template = get_template_from_string(tpl)
        category = self.new_category()
        context = Context({})
        self.assertEqual(template.render(context), 'Test category')

    def test_get_invalid_category_name(self):
        tpl = """{% load pages_tags category_tags %}{% category_name 'enoent' %}"""
        template = get_template_from_string(tpl)
        category = self.new_category()
        context = Context({})
        self.assertEqual(template.render(context), '')

    def test_get_category(self):
        tpl = """{% load pages_tags category_tags %}{% get_category 'test-category' %}{{ category.title }}"""
        template = get_template_from_string(tpl)
        category = self.new_category()
        context = Context({})
        self.assertEqual(template.render(context), 'Test category')

    # functionnal tests
        
    def test_get_invalidcategory(self):
        tpl = """{% load pages_tags category_tags %}{% get_category 'enoent' %}{{ category.title }}"""
        template = get_template_from_string(tpl)
        category = self.new_category()
        context = Context({})
        self.assertEqual(template.render(context), 'Enoent')
        
    def test_add_category(self):
        """Add category page properly shown"""
        c = self.get_admin_client()

        response = c.get('/admin/category/category/add/')
        self.assertEqual(response.status_code, 200)

    def test_create_category(self):
        """Test category gets created"""
        c = self.get_admin_client()

        category_data = self.get_new_category_data()
        response = c.post('/admin/category/category/add/', category_data)
        self.assertRedirects(response, '/admin/category/category/')
        category = Category.objects.latest('id')
        self.assertEqual(category.title, category_data['title'])
        self.assertEqual(category.slug, category_data['slug'])
        self.assertEqual(category.get_pages().count(), 0)
        
    def test_category_slug_collision(self):
        """Category slugs collide"""
        self.set_setting("PAGE_UNIQUE_SLUG_REQUIRED", False)

        c = self.get_admin_client()

        category_data = self.get_new_category_data()
        response = c.post('/admin/category/category/add/', category_data)
        self.assertRedirects(response, '/admin/category/category/')

        self.set_setting("PAGE_UNIQUE_SLUG_REQUIRED", True)
        response = c.post('/admin/category/category/add/', category_data)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(Category.objects.all().count(), 1)
        
    def test_category_change_on_page(self):
        """Test changing a page's category"""
        c = self.get_admin_client()

        # Set it up
        category_data = self.get_new_category_data()
        response = c.post('/admin/category/category/add/', category_data)
        self.assertRedirects(response, '/admin/category/category/')
        self.assertEqual(Category.objects.all().count(), 1)

        category_data = self.get_new_category_data()
        response = c.post('/admin/category/category/add/', category_data)
        self.assertRedirects(response, '/admin/category/category/')
        self.assertEqual(Category.objects.all().count(), 2)

        cat1, cat2 = Category.objects.all()
        self.assertNotEqual(cat1.slug, cat2.slug)

        # Create page
        page_data = self.get_new_page_data()
        page_data['category'] = 'test-category-1'
        response = c.post('/admin/pages/page/add/', page_data)
        self.assertRedirects(response, '/admin/pages/page/')
        slug_content = Content.objects.get_content_slug_by_slug(
            page_data['slug']
        )
        assert(slug_content is not None)
        page = slug_content.page
        language = 'en-us'
        content = page.get_content(language, 'category')
        assert(not not content)
        cats = page.content_set.filter(language=language, type='category')
        self.assertEqual(cats.count(), 1)

        # Edit it
        page_data['category'] = 'test-category-2'
        response = c.post('/admin/pages/page/%d/' % page.id, page_data)
        self.assertRedirects(response, '/admin/pages/page/')
        page = Page.objects.get(id=page.id)
        cats = page.content_set.filter(language=language, type='category')
        self.assertEqual(cats.count(), 1)
        
    def test_category_slug_renaming(self):
        """Test renaming a category slug"""
        self.set_setting("PAGE_AUTOMATIC_SLUG_RENAMING", True)

        c = self.get_admin_client()
        category_data = self.get_new_category_data()

        response = c.post('/admin/category/category/add/', category_data)
        self.assertRedirects(response, '/admin/category/category/')
        self.assertEqual(Category.objects.all().count(), 1)

        response = c.post('/admin/category/category/add/', category_data)
        self.assertRedirects(response, '/admin/category/category/')
        self.assertEqual(Category.objects.all().count(), 2)

        cat1, cat2 = Category.objects.all()
        self.assertNotEqual(cat1.slug, cat2.slug)
