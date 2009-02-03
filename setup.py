from distutils.core import setup
import glob

datas = [ "locale/" + l.rsplit('/')[-1]+"/LC_MESSAGES/*.*" for l in glob.glob("pages/locale/*")]
datas.extend([
    'templates/admin/pages/page/*.html',
    'templates/pages/*.html',
    'fixtures/*.json'
    ]
)

setup(
    name='django-page-cms',
    version=__import__('pages').__version__,
    description='A tree based Django CMS application',
    author='Batiste Bieler',
    author_email='batiste.bieler@gmail.com',
    url='http://code.google.com/p/django-page-cms/',
    requires=('html5lib (>=0.10)', 'tagging (>=0.2.1)', 'django_mptt (>=0.2.1)', ),
    packages=[
        'pages',
        'pages.admin',
        'pages.templatetags',
        #'example',
    ],
    package_dir={'pages': 'pages', 'pages.locale': 'locale', 'pages.templates': 'templates'},
    package_data={'pages': datas},
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
        'Programming Language :: Python :: 2.3',
        'Programming Language :: JavaScript',
        'Topic :: Internet :: WWW/HTTP :: Site Management',
    ]
)
