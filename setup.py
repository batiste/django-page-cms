# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from pkg_resources import require, DistributionNotFound
import pages
import os
package_name = 'django-page-cms'


def local_open(fname):
    return open(os.path.join(os.path.dirname(__file__), fname))


data_dirs = []
for directory in os.walk('pages/templates'):
    data_dirs.append(directory[0][6:] + '/*.*')

for directory in os.walk('pages/media'):
    data_dirs.append(directory[0][6:] + '/*.*')

for directory in os.walk('pages/static'):
    data_dirs.append(directory[0][6:] + '/*.*')

for directory in os.walk('pages/locale'):
    data_dirs.append(directory[0][6:] + '/*.*')

for directory in os.walk('pages/fixtures'):
    data_dirs.append(directory[0][6:] + '/*.*')

example_dirs = []
for directory in os.walk('example/templates'):
    example_dirs.append(directory[0][8:] + '/*.*')

url_schema = 'http://pypi.python.org/packages/source/d/%s/%s-%s.tar.gz'
download_url = url_schema % (package_name, package_name, pages.__version__)

install_requires = [
    'django-mptt>=0.8.3,<0.9.0',
    'six>=1.10.0,<1.11.0',
    'Pillow>=3.2.0,<3.3.0',
    'tqdm>=4.4.0,<4.5.0',
    'django-taggit>=0.18.1,<0.19.0',
    'requests>=2.9.0,<3.0.0',
]

extra = [
    'django-haystack',
    'Markdown>=2.6.6,<2.7.0',
    'Whoosh>=2.7.4,<2.8.0',
    'django-ckeditor>=5.0.3,<5.1.0',
    'polib>=1.0.7,<1.1.0',
    'djangorestframework>=3.3.2,<3.4.0'
]

tests_require = [
    'selenium',
    'coverage'
]

extras_require = {
    'extra': extra,
    'tests': install_requires + extra + tests_require,
    'full': install_requires + extra + ['Django>=1.8,<1.10']
}

dependency_links=[
    'git+ssh://git@github.com/django-haystack/django-haystack.git@42f53cda9a770ff7daf2ff792cbcab5cd843e2a7#egg=django-haystack'
]

setup(
    name=package_name,
    test_suite='pages.test_runner.build_suite',
    version=pages.__version__,
    description=pages.__doc__,
    author=pages.__author__,
    author_email=pages.__contact__,
    url=pages.__homepage__,
    license=pages.__license__,
    long_description=local_open('README.rst').read(),
    download_url=download_url,
    install_requires=install_requires,
    extras_require=extras_require,
    tests_require=tests_require,
    dependency_links=dependency_links,
    packages=find_packages(),
    # very important for the binary distribution to include the templates.
    package_data={'pages': data_dirs, 'example': example_dirs},
    #include_package_data=True, # include package data under svn source control
    zip_safe=False,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: JavaScript',
        'Topic :: Internet :: WWW/HTTP :: Site Management'
    ],
    entry_points={
        'console_scripts': ['gerbi=pages.command_line:main'],
    }
)
