from django import template
from ..pages.models import Language, Content, Page
from ..hierarchical.models import HierarchicalNode, HierarchicalObject
register = template.Library()

@register.inclusion_tag('menu.html', takes_context=True)
def show_menu(context, page, url='/'):
    """TODO: Very inneficient code tag"""
    nodes = HierarchicalNode.get_nodes_by_object(page)
    if len(nodes) > 0:
        children = nodes[0].get_children_objects(page)
    request = context['request']
    if 'current_page' in context:
        current_page = context['current_page']
        is_parent = HierarchicalNode.is_parent(page, current_page)
    return locals()

@register.inclusion_tag('sub_menu.html', takes_context=True)
def show_sub_menu(context, page, url='/'):
    """TODO: Very inneficient code tag"""
    root = HierarchicalNode.get_root_object(page)
    children = HierarchicalNode.get_children_objects(root)
    request = context['request']
    if 'current_page' in context:
        current_page = context['current_page']
        is_parent = HierarchicalNode.is_parent(page, current_page)
    return locals()
    
@register.inclusion_tag('pages/content.html', takes_context=True)
def show_content(context, page, content_type):
    l = Language.get_from_request(context['request'])
    request = context['request']
    c = Content.get_content(page, l, content_type, True)
    if c:
        return {'content':c}
    return {'content':''}

def do_placeholder(parser, token):
    try:
        # split_contents() knows not to split quoted strings.
        tag_name, page, name, widget = token.split_contents()
    except ValueError:
        msg = '%r tag requires three arguments' % token.contents[0]
        raise template.TemplateSyntaxError(msg)
    return PlaceholderNode(page, name, widget)

class PlaceholderNode(template.Node):

    def __init__(self, name, page, widget):
        self.page = page
        self.name = name
        self.widget = widget

    def render(self, context):
        if not 'request' in context or not self.page in context:
            return ''
        l = Language.get_from_request(context['request'])
        request = context['request']
        c = Content.get_content(context[self.page], l, self.name, True)
        if c:
            return c
        
    def __repr__(self):
        return "<Placeholder Node: %s>" % self.name

register.tag('placeholder', do_placeholder)
