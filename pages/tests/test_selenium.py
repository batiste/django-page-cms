# -*- coding: utf-8 -*-
"""Django page CMS selemium test module"""
from pages.models import Page
from pages.tests.testcase import TestCase
from pages import settings
from django.core.urlresolvers import reverse
from django.test import LiveServerTestCase
from django.contrib import auth

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


screenshot_nb = 1


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

    def screenshot(self):
        global screenshot_nb
        if settings.PAGE_TESTS_SAVE_SCREENSHOTS:
            self.browser.save_screenshot('screenshot_%d.png' % screenshot_nb)
            screenshot_nb += 1

    def select_option(self, select, option_id):
        for option in select.find_elements_by_tag_name('option'):
            if option.get_attribute('value') == str(option_id):
                option.click()

    def visit(self, url):
        # Open the django admin page.
        # DjangoLiveServerTestCase provides a live server url attribute
        # to access the base url in tests
        url = '%s%s' % (self.live_server_url,  url)
        self.browser.get(url)

    def click(self, selector):
        return self.browser.find_element_by_css_selector(selector).click()

    def wait(self, id):
        return WebDriverWait(self.browser, 3).until(
            EC.presence_of_element_located((By.ID, id)))

    def login(self):
        self.visit("/admin/")
        # Fill login information of admin
        username = self.browser.find_element_by_id("id_username")
        username.send_keys("admin_s")
        password = self.browser.find_element_by_id("id_password")
        password.send_keys("admin")
        self.click("input[type='submit']")

    def tearDown(self):
        self.browser.quit()
        super(SeleniumTestCase, self).tearDown()

    def url_change(self, id):
        return reverse('admin:pages_page_change', args=[id])

    def test_admin_select(self):
        self.login()
        page = self.new_page()
        self.visit(self.url_change(page.id))
        status = self.browser.find_element_by_id('id_status')
        self.assertEqual(status.get_attribute('value'), str(page.status))

        self.select_option(status, str(Page.DRAFT))
        self.assertEqual(status.get_attribute('value'), str(Page.DRAFT))

        src = self.browser.find_element_by_css_selector('.status'
            ).find_element_by_tag_name('img'
            ).get_attribute('src')

        self.assertTrue(src.endswith('draft.gif'))

    def test_admin_move_page(self):
        self.login()
        page_1 = self.new_page({'slug':'p1'})
        page_2 = self.new_page({'slug':'p2'})
        self.visit(reverse('admin:pages_page_changelist'))

        h1 = self.browser.find_element_by_css_selector('#content h1')
        self.assertEqual(h1.text, 'Select page to change')

        rows = self.browser.find_elements_by_css_selector('#page-list tbody tr')
        row_1 = rows[0]
        row_2 = rows[1]

        self.assertEqual(row_1.get_attribute('id'), 'page-row-%d' % page_1.id)
        self.assertEqual(row_2.get_attribute('id'), 'page-row-%d' % page_2.id)

        page_3 = self.new_page({'slug':'p3'})

        self.click('#move-link-%d' % page_2.id)
        self.click('#move-target-%d .move-target.left' % page_1.id)

        self.wait('page-row-%d' % page_3.id)

        rows = self.browser.find_elements_by_css_selector('#page-list tbody tr')
        row_1 = rows[0]
        row_2 = rows[1]
        row_3 = rows[2]

        self.screenshot()

        self.assertEqual(row_1.get_attribute('id'), 'page-row-%d' % page_2.id)
        self.assertEqual(row_2.get_attribute('id'), 'page-row-%d' % page_1.id)
        self.assertEqual(row_3.get_attribute('id'), 'page-row-%d' % page_3.id)
