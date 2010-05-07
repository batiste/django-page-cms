
import os, sys
try:
    from coverage import coverage
except ImportError:
    coverage = None
coverage = None
import fnmatch

# necessary for "python setup.py test"

patterns = (
    "pages.migrations.*",
    "pages.tests.*",
    "pages.testproj.*",
    "pages.urls",
    "pages.__init__",
    "pages.search_indexes",
    "pages.test_runner",
)

def match_pattern(filename):
    for pattern in patterns:
        if fnmatch.fnmatch(filename, pattern):
            return True
    return False

def get_all_coverage_modules(app_module, exclude_patterns=[]):
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
        for filename in files:
            if filename.lower().endswith('.py'):
                mod_name = filename[:-3].lower()
                path = '.'.join(root_path + [mod_name])
                if not match_pattern(path):
                    try:
                        mod = __import__(path, {}, {}, mod_name)
                    except ImportError:
                        pass
                    else:
                        mod_list.append(mod)

    return mod_list

def run_tests(test_labels=('pages',), verbosity=1, interactive=True,
        extra_tests=[]):

    os.environ['DJANGO_SETTINGS_MODULE'] = 'pages.testproj.test_settings'
    current_dirname = os.path.dirname(__file__)
    sys.path.insert(0, current_dirname)
    sys.path.insert(0, os.path.join(current_dirname, '../..'))


    from django.test.simple import run_tests as django_test_runner
    from django.db.models import get_app, get_apps

    if coverage:
        cov = coverage()
        cov.erase()
        cov.use_cache(0)
        cov.start()
        
    results = django_test_runner(test_labels, verbosity, interactive,
        extra_tests)

    if coverage:
        cov.stop()
        app = get_app('pages')
        modules = get_all_coverage_modules(app)
        cov.html_report(modules, directory='coverage')

    sys.exit(results)
    

if __name__ == '__main__':
    run_tests()