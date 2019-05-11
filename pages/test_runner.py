import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pages.testproj.test_settings")
current_dirname = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(current_dirname, '..'))

import django
django.setup()

from django.test.runner import DiscoverRunner
from django.core.management import call_command

class PageTestSuiteRunner(DiscoverRunner):

    def run_tests(self, test_labels=('pages',), extra_tests=None):
        call_command('collectstatic', '--noinput')
        results = DiscoverRunner.run_tests(self, test_labels, extra_tests)
        sys.exit(results)

if __name__ == '__main__':
    runner = PageTestSuiteRunner(failfast=True)
    if len(sys.argv) > 1:
        runner.run_tests(test_labels=(sys.argv[1], ))
    else:
        runner.run_tests()
