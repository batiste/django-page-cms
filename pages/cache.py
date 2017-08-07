# -*- coding: utf-8 -*-

from django.core.cache import caches
from django.core.cache.backends.base import InvalidCacheBackendError

try:
    cache = caches['pages']
except InvalidCacheBackendError:
    cache = caches['default']
