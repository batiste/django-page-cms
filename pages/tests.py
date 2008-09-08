from django.test import TestCase
from pages.models import *

class PagesTestCase(TestCase):
    fixtures = ['tests']

    def test_01(self):
        assert(1==1)
        pass
        
