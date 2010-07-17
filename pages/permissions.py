"""Django page CMS permissions management using django-authority."""

import authority

from pages.models import Page
from pages import settings

permission_checks = []
for perm_lang in settings.PAGE_LANGUAGES:
    permission_checks.append('manage ('+perm_lang[0]+')')

permission_checks = permission_checks + ['freeze', 'manage hierarchy']

class PagePermission(authority.permissions.BasePermission):
    """Handle the :class:`Page <pages.models.Page>` permissions."""
    label = 'page_permission'
    checks = permission_checks

    def check(self, action, page=None, lang=None, method=None):
        """Return ``True`` if the current user has permission on the page."""
        if self.user.is_superuser:
            return True
        
        if action == 'change':
            return self.has_change_permission(page, lang, method)
            
        if action == 'delete':
            if not self.delete_page():
                return False
            return True
        if action == 'add':
            if not self.add_page():
                return False
            return True
        if action == 'freeze':
            perm = self.user.has_perm('pages.can_freeze')
            if perm:
                return True
            return False
        if action == 'publish':
            perm = self.user.has_perm('pages.can_publish')
            if perm:
                return True
            return False
        
        return False

    def has_change_permission(self, page, lang, method=None):
        """Return ``True`` if the current user has permission to
        change the page."""
        
        # the user has always the right to look at a page content
        # if he doesn't try to modify it.
        if method != 'POST':
            return True
            
        # right to change all the pages
        if self.change_page():
            return True
        if lang:
            # try the global language permission first
            perm = self.user.has_perm(
                'pages.can_manage_%s' % lang.replace('-', '_')
            )
            if perm:
                return True
            # then per object permission
            perm_func = getattr(self, 'manage (%s)_page' % lang)
            if perm_func(page):
                return True
        # last hierarchic permissions because it's more expensive
        perm_func = getattr(self, 'manage hierarchy_page')
        if perm_func(page):
            return True
        else:
            for ancestor in page.get_ancestors():
                if perm_func(ancestor):
                    return True

        # everything else failed, no permissions
        return False


authority.register(Page, PagePermission)