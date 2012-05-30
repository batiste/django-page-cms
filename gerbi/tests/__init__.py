"""Django page CMS test suite module"""
import unittest
from gerbi.tests.test_functionnal import FunctionnalTestCase
from gerbi.tests.test_unit import UnitTestCase
from gerbi.tests.test_regression import RegressionTestCase

def suite():
    suite = unittest.TestSuite()
    from gerbi import settings
    if not settings.GERBI_ENABLE_TESTS:
        return suite
    suite.addTest(unittest.makeSuite(UnitTestCase))
    suite.addTest(unittest.makeSuite(RegressionTestCase))
    suite.addTest(unittest.makeSuite(LinkTestCase))
    suite.addTest(unittest.makeSuite(AutoRenderTestCase))
    # being the slower test I run it at the end
    suite.addTest(unittest.makeSuite(FunctionnalTestCase))
    return suite
