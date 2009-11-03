from coverage import coverage
import os, sys
os.environ['DJANGO_SETTINGS_MODULE'] = 'example.settings'
from inspect import getmembers, ismodule

from django.conf import settings
from django.test.simple import run_tests as django_test_runner
from django.db.models import get_app, get_apps

test_dir = os.path.dirname(__file__)
sys.path.insert(0, test_dir)

def get_all_coverage_modules(app_module, exclude_files=[]):
    """Returns all possible modules to report coverage on, even if they
    aren't loaded.
    """
    # We start off with the imported models.py, so we need to import
    # the parent app package to find the path.
    app_path = app_module.__name__.split('.')[:-1]
    app_package = __import__('.'.join(app_path), {}, {}, app_path[-1])
    app_dirpath = app_package.__path__[-1]

    mod_list = []
    for root, dirs, files in os.walk(app_dirpath):
        root_path = app_path + root[len(app_dirpath):].split(os.path.sep)[1:]
        if not '.svn' in root_path and not 'tests' in root_path:
            for file in files:
                if file not in exclude_files:
                    if file.lower().endswith('.py'):
                        mod_name = file[:-3].lower()
                        try:
                            mod = __import__('.'.join(root_path + [mod_name]),
                                {}, {}, mod_name)
                        except ImportError:
                            pass
                        else:
                            mod_list.append(mod)

    return mod_list


def run_tests(test_labels=('pages',), verbosity=1, interactive=True,
        extra_tests=[]):
    cov = coverage()
    cov.erase()
    cov.use_cache(0)
    cov.start()
    app = get_app('pages')
    modules = get_all_coverage_modules(app, exclude_files=['auto_render.py'])
    results = django_test_runner(test_labels, verbosity, interactive,
        extra_tests)
    cov.stop()
    cov.html_report(modules, directory='coverage')
    sys.exit(results)

