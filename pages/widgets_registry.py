"""Django page CMS widget registry."""
from django.utils.translation import ugettext as _

__all__ = ('register_widget',)


class WidgetAlreadyRegistered(Exception):
    """
    An attempt was made to register a widget for Django page CMS more
    than once.
    """
    pass


class WidgetNotFound(Exception):
    """
    The requested widget was not found
    """
    pass

registry = []


def register_widget(widget):
    """
    Register the given widget as a candidate to use in placeholder.
    """
    if widget in registry:
        raise WidgetAlreadyRegistered(
            _('The widget %s has already been registered.') % widget.__name__)
    registry.append(widget)


def get_widget(name):
    """
    Give back a widget class according to his name.
    """
    for widget in registry:
        if widget.__name__ == name:
            return widget
    raise WidgetNotFound(
        _('The widget %s has not been registered.') % name)
