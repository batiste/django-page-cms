# -*- coding: utf-8 -*-
"""Django page CMS selemium test module"""
import django

from django.conf import settings
from pages.models import Page, Content
from pages.tests.testcase import TestCase
from django.core.urlresolvers import reverse
from django.test import LiveServerTestCase
from django.contrib import auth

from selenium import webdriver
from selenium.webdriver import PhantomJS

class SeleniumTestCase(TestCase, LiveServerTestCase):

    def setUp(self):
        self.browser = webdriver.PhantomJS()
        client = self.get_admin_client()

        # setUp is where you instantiate the selenium webdriver and loads the browser.
        auth.models.User.objects.create_superuser(
            username='admin_s',
            password='admin',
            email='admin_s@example.com'
        )

        self.browser.get('%s%s' % (self.live_server_url,  "/admin/"))

        super(SeleniumTestCase, self).setUp()

    def select_option(self, select, option_id):
        for option in select.find_elements_by_tag_name('option'):
            if option.get_attribute('value') == str(option_id):
                option.click()

    def login(self):
        # Open the django admin page.
        # DjangoLiveServerTestCase provides a live server url attribute
        # to access the base url in tests
        self.browser.get(
            '%s%s' % (self.live_server_url,  "/admin/")
        )

        # Fill login information of admin
        username = self.browser.find_element_by_id("id_username")
        username.send_keys("admin_s")
        password = self.browser.find_element_by_id("id_password")
        password.send_keys("admin")
        self.browser.find_element_by_css_selector("input[type='submit']").click()

    def tearDown(self):
        self.browser.quit()
        super(SeleniumTestCase, self).tearDown()

    def url_change(self, id):
        return '%s%s' % (self.live_server_url,
            reverse('admin:pages_page_change',  args=[id]))

    def test_admin_select(self):
        self.login()
        page = self.new_page()
        self.browser.get(self.url_change(page.id))
        #self.browser.save_screenshot('screenie.png')
        status = self.browser.find_element_by_id('id_status')
        self.assertEqual(status.get_attribute('value'), str(page.status))

        self.select_option(status, str(Page.DRAFT))
        self.assertEqual(status.get_attribute('value'), str(Page.DRAFT))

        #src = self.browser.find_element_by_css_selector('.status'
        #    ).find_element_by_tag_name('img'
        #    ).get_attribute('src')

        #self.assertTrue(src.endswith('draft.gif'))
