from django import template
register = template.Library()

"""@register.inclusion_tag('menu.html', takes_context=True)
def show_menu(context, node, url='/'):
    children = node.children.filter(status=1)
    request = context['request']
    return locals()"""

@register.inclusion_tag('hierarchical/admin_menu.html', takes_context=True)
def show_admin_menu(context, node, url='/admin/hierarchical/hierarchicalnode/', level=None):
    children = node.children.all()
    request = context['request']
    if level is None:
        level = 0
    else:
        level = level+2
    return locals()

@register.filter(name='truncateletters')
def truncateletters(value, arg):
    """
    Truncates a string after a certain number of letters

    Argument: Number of letters to truncate after
    """
    def truncate_letters(s, num):
        "Truncates a string after a certain number of letters."
        length = int(num)
        letters = [l for l in s]
        if len(letters) > length:
            letters = letters[:length]
            if not letters[-3:] == ['.','.','.']:
                letters += ['.','.','.']
        return ''.join(letters)

    try:
        length = int(arg)
    except ValueError: # invalid literal for int()
        return value # Fail silently
    if not isinstance(value, basestring):
        value = str(value)
    return truncate_letters(value, length)