from pages.models import Page

from django.utils.translation import ugettext_lazy as _
from authority.permissions import BasePermission

import authority

from pages.settings import PAGE_LANGUAGES

languages = []
for lang in PAGE_LANGUAGES:
    languages.append('manage ('+lang[0]+')')

permission_checks = languages + ['freeze']

class PagePermission(BasePermission):
    label = 'page_permission'
    checks = permission_checks

    


authority.register(Page, PagePermission)