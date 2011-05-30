"""Django page CMS urlconf registry."""
from django.utils.translation import ugettext as _


class UrlconfAlreadyRegistered(Exception):
    """
    An attempt was made to register a urlconf for Django page CMS more
    than once.
    """


class UrlconfNotFound(Exception):
    """
    The requested urlconf was not found
    """

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
            raise UrlconfAlreadyRegistered(
                _('The urlconf %s has already been registered.') % name)
    urlconf_tuple = (name, urlconf, label, urlconf)
    registry.append(urlconf_tuple)


def get_urlconf(name):
    for urlconf_tuple in registry:
        if urlconf_tuple[0] == name:
            return urlconf_tuple[1]
    raise UrlconfNotFound(
        _('The urlconf %s has not been registered.') % name)
