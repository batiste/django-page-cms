"""Django page CMS test suite module"""
import unittest
from django_gerbi.tests.test_functionnal import FunctionnalTestCase
from django_gerbi.tests.test_unit import UnitTestCase
from django_gerbi.tests.test_regression import RegressionTestCase
from django_gerbi.tests.test_pages_link import LinkTestCase
from django_gerbi.tests.test_auto_render import AutoRenderTestCase

def suite():
    suite = unittest.TestSuite()
    from django_gerbi import settings
    if not settings.GERBI_ENABLE_TESTS:
        return suite
    suite.addTest(unittest.makeSuite(UnitTestCase))
    suite.addTest(unittest.makeSuite(RegressionTestCase))
    suite.addTest(unittest.makeSuite(LinkTestCase))
    suite.addTest(unittest.makeSuite(AutoRenderTestCase))
    # being the slower test I run it at the end
    suite.addTest(unittest.makeSuite(FunctionnalTestCase))
    return suite
