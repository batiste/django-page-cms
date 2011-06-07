# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from pkg_resources import require, DistributionNotFound
import gerbi
import os
package_name = 'django-gerbi'
module_name = 'gerbi'

def local_open(fname):
    return open(os.path.join(os.path.dirname(__file__), fname))

requirements = local_open('requirements/external_apps.txt')

# Build the list of dependency to install
required_to_install = []
for dist in requirements.readlines():
    dist = dist.strip()
    try:
        require(dist)
    except DistributionNotFound:
        required_to_install.append(dist)

data_dirs = []
for directory in os.walk( module_name + os.sep + 'templates' ):
    # data_dirs.append(directory[0][6:] + '/*.*')
    data_dirs.append( os.path.sep.join( directory[0].split(os.sep)[1:] ) + os.sep + '*.*')

for directory in os.walk( module_name + os.sep + 'media'):
    # data_dirs.append(directory[0][6:] + '/*.*')
    data_dirs.append( os.path.sep.join( directory[0].split(os.sep)[1:] ) + os.sep + '*.*')

for directory in os.walk( module_name + os.sep + 'static'):
    # data_dirs.append(directory[0][6:] + '/*.*')
    data_dirs.append( os.path.sep.join( directory[0].split(os.sep)[1:] ) + os.sep + '*.*')

url_schema = 'http://pypi.python.org/packages/source/d/%s/%s-%s.tar.gz'
download_url = url_schema % (package_name, package_name, gerbi.__version__)

setup(
    name=package_name,
    test_suite= module_name + '.test_runner.run_tests',
    version=gerbi.__version__,
    description=gerbi.__doc__,
    author=gerbi.__author__,
    author_email=gerbi.__contact__,
    url=gerbi.__homepage__,
    license=gerbi.__license__,
    long_description=local_open('README.rst').read(),
    download_url=download_url,
    install_requires=required_to_install,
    packages=find_packages(exclude=['example', 'example.*']),
    # very important for the binary distribution to include the templates.
    package_data={module_name: data_dirs},
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
        'Programming Language :: Python :: 2.3',
        'Programming Language :: JavaScript',
        'Topic :: Internet :: WWW/HTTP :: Site Management',
    ],
)
