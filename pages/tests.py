from django.test import TestCase
from pages.models import *

class PagesTestCase(TestCase):
    fixtures = ['tests']

    def test_01_managers(self):
        """Check the managers"""
        pages = Page.published.all()
        for p in pages:
            self.assertEqual(p.status, 1)
        pages = Page.drafts.all()
        for p in pages:
            self.assertEqual(p.status, 0)
            
    def test_02_template_inheritance(self):
        """Check if the template inheritance is working right"""
        for p in Page.objects.all():
            if p.template == '' and not p.get_template() == None:
                #there is a parent with a template, go find it
                parent = p.parent
                while True:
                    if parent.template:
                        break
                    parent = p.parent
                #the page must have inherited of it's parent template
                self.assertEqual(parent.template, p.get_template())
                
    def test_03_content(self):
        """Check if there is always one content a least by page"""
        for p in Page.objects.all():
            for l in Language.objects.all():
                if Content.get_content(p, l, 0) == None:
                    # if there is no content in this, there must at least have something 
                    # in another one
                    self.assertNotEqual(Content.get_content(p, l, 0, True), None)
                    
    def test_03_order(self):
        """The order of a new page must be the greatest across his brothers"""
        user = User.objects.get(pk=1)
        page = Page(author=user, slug="just-a-test")
        page.save()
        self.assertTrue(page.is_last())
        max = page.order
        for p in page.brothers():
            if p.order > max:
                max = p.order
        self.assertEqual(max, page.order)
        