import os
import sys
coverage_module_present = True
try:
    from coverage import coverage
except ImportError:
    coverage_module_present = False

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pages.testproj.test_settings")
current_dirname = os.path.dirname(__file__)
#sys.path.insert(0, current_dirname)
sys.path.insert(0, os.path.join(current_dirname, '..'))

import django
django.setup()

from django.test.runner import DiscoverRunner
from django.contrib.admin.sites import AlreadyRegistered

class PageTestSuiteRunner(DiscoverRunner):

    def run_tests(self, test_labels=('pages',), extra_tests=None):
        results = DiscoverRunner.run_tests(self, test_labels, extra_tests)
        sys.exit(results)

def build_suite():
    runner = PageTestSuiteRunner()
    runner.setup_test_environment()
    runner.setup_databases()
    return runner.build_suite(test_labels=('pages',), extra_tests=None)

if __name__ == '__main__':
    runner = PageTestSuiteRunner(failfast=False)
    if len(sys.argv) > 1:
        runner.run_tests(test_labels=(sys.argv[1], ))
    else:
        runner.run_tests()
