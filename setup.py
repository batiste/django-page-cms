from distutils.core import setup

setup(
    name='django-page-cms',
    version=__import__('pages').__version__,
    description='A tree based Django CMS application',
    author='Batiste Bieler',
    author_email='batiste.bieler@gmail.com',
    url='http://code.google.com/p/django-page-cms/',
    packages=[
        'pages',
        'pages.admin',
        'pages.templatetags',
        'example',
    ],
    package_dir={'pages': 'pages'},
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ]
)
