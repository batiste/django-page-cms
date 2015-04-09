# -*- coding: utf-8 -*-

from django.core.cache import caches

if hasattr(caches, 'pages'):
	cache = caches['pages']
else:
	cache = caches['default']

