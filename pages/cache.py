# -*- coding: utf-8 -*-

from django.core import cache as cache_module

# Wrapper to get the cache we want
from . import settings

cache = cache_module.get_cache(settings.PAGE_CACHE_LOCATION)

