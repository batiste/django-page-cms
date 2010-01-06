__all__ = ('register_urlconf',)
from django.utils.translation import ugettext as _

class UrlconfAlreadyRegistered(Exception):
    """
    An attempt was made to register a widget for Django page CMS more
    than once.
    """
    pass

class UrlconfNotFound(Exception):
    """
    The requested widget was not found
    """
    pass

registry = []

def get_choices():
    choices = [('', 'No delegation')]
    for reg in registry:
        if reg[2]:
            label = reg[2]
        else:
            label = reg[0]
        choices.append((reg[0], label))
    return choices

def register_urlconf(name, urlconf, label=None):
    for urlconf_tuple in registry:
        if urlconf_tuple[0] == name:
            raise urlconfAlreadyRegistered(
                _('The urlconf %s has already been registered.') % name)
    urlconf_tuple = (name, urlconf, label, urlconf)
    registry.append(urlconf_tuple)

def get_urlconf(name):
    for urlconf_tuple in registry:
        if urlconf_tuple[0] == name:
            return urlconf_tuple[1]
    raise urlconfNotFound(
        _('The urlconf %s has not been registered.') % name)