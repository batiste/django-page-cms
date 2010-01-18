from pages.models import Page
from pages import settings

from django.utils.translation import ugettext_lazy as _

import authority

languages = []
for lang in settings.PAGE_LANGUAGES:
    languages.append('manage ('+lang[0]+')')


permission_checks = languages + ['freeze']

class PagePermission(authority.permissions.BasePermission):
    label = 'page_permission'
    checks = permission_checks

    def check(self, action, page=None, lang=None, method=None):
        """Return ``True`` if the current user has permission on the page."""
        if action == 'change':
            if not self.change_page():
                return False
            if settings.PAGE_PERMISSION == False:
                return True
            if lang and method=='POST':
                func = getattr(self, 'manage (%s)_page' % lang)
                if not func(page):
                    return False
            return True
        if action == 'delete':
            if not self.delete_page():
                return False
            return True
        if action == 'add':
            if not self.add_page():
                return False
            return True
        if action == 'freeze':
            if not self.freeze():
                return False
            return True
        return False

    def freeze(self):
        return True

authority.register(Page, PagePermission)