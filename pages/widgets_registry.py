__all__ = ('register_widget',)
from django.utils.translation import ugettext as _

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

    if widget in registry:
        raise AlreadyRegistered(
            _('The widget %s has already been registered.') % widget.__name__)
    registry.append(widget)

def get_widget(name):

    for widget in registry:
        if widget.__name__ == name:
            return widget
    raise WidgetNotFound(
        _('The widget %s has not been registered.') % name)