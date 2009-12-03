# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='django-page-cms',
    test_suite = "example.test_runner.run_tests",
    test_requires = (
        'coverage',
    ),
    version=__import__('pages').__version__,
    description='A tree based Django CMS application',
    author='Batiste Bieler',
    author_email='batiste.bieler@gmail.com',
    url='http://code.google.com/p/django-page-cms/',
    download_url='http://code.google.com/p/django-page-cms/downloads/list',
    requires=(
        'BeautifulSoup',
        'Django',
        'html5lib (>=0.10)',
        'tagging (>0.2.1)', # please use the trunk version of tagging
        'django_mptt (>0.2.1)', # please use the trunk version of django mptt
    ),
    packages=find_packages(exclude=['example', 'example.*']),
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
