# -*- coding: utf-8 -*-
"""Django page CMS module."""
VERSION = (2, 0, 8)
__version__ = '.'.join(map(str, VERSION))
__author__ = "Batiste Bieler"
__contact__ = "batiste.bieler@gmail.com"
__homepage__ = "https://github.com/batiste/django-page-cms"
__docformat__ = "restructuredtext"
__doc__ = 'A tree based Django CMS application'
__license__ = 'BSD'
__keywords__ = ['django', 'cms']

default_app_config = 'pages.app_config.BasicCmsConfig'
