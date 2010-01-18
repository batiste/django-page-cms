from pages.models import Page
from pages import settings

from django.utils.translation import ugettext_lazy as _

import authority

permission_checks = []
for lang in settings.PAGE_LANGUAGES:
    permission_checks.append('manage ('+lang[0]+')')

permission_checks = permission_checks + ['freeze']

class PagePermission(authority.permissions.BasePermission):
    label = 'page_permission'
    checks = permission_checks

    def check(self, action, page=None, lang=None, method=None):
        """Return ``True`` if the current user has permission on the page."""
        if action=='change':
            if method=='POST':
                if self.change_page():
                    return True
                if lang and method=='POST':
                    # try the global language permission first
                    print 'pages.can_manage_%s' % lang.replace('-', '_')
                    perm = self.user.has_perm(
                        'pages.can_manage_%s' % lang.replace('-', '_')
                    )
                    print perm
                    if perm:
                        return True
                    # then per object permission
                    func = getattr(self, 'manage (%s)_page' % lang)
                    if func(page):
                        return True
                return False
            else:
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