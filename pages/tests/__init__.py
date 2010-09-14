"""Django page CMS test suite module"""
import unittest

def suite():
    suite = unittest.TestSuite()
    from pages.tests.test_functionnal import FunctionnalTestCase
    from pages.tests.test_unit import UnitTestCase
    from pages.tests.test_regression import RegressionTestCase
    from pages.tests.test_pages_link import LinkTestCase
    from pages.tests.test_auto_render import AutoRenderTestCase
    suite.addTest(unittest.makeSuite(FunctionnalTestCase))
    suite.addTest(unittest.makeSuite(UnitTestCase))
    suite.addTest(unittest.makeSuite(RegressionTestCase))
    suite.addTest(unittest.makeSuite(LinkTestCase))
    suite.addTest(unittest.makeSuite(AutoRenderTestCase))
    return suite
