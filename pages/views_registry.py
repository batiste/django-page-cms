__all__ = ('view_register',)
from django.utils.translation import ugettext as _

class ViewAlreadyRegistered(Exception):
    """
    An attempt was made to register a widget for Django page CMS more than once.
    """
    pass

class ViewNotFound(Exception):
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

def register_view(name, view, label=None):
    for view_tuple in registry:
        if view_tuple[0] == name:
            raise AlreadyRegistered(
                _('The view %s has already been registered.') % name)
    view_tuple = (name, view, label)
    registry.append(view_tuple)

def get_view(name):
    for view_tuple in registry:
        if view_tuple[0] == name:
            return view_tuple[1]
    raise WidgetNotFound(
        _('The widget %s has not been registered.') % name)