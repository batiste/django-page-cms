from django import template
#import pages.models
#from pages.models import Language, Content, Page
from ..pages.models import Language, Content, Page
from ..hierarchical.models import HierarchicalNode, HierarchicalObject
register = template.Library()

@register.inclusion_tag('menu.html', takes_context=True)
def show_menu(context, page, url='/'):
    nodes = HierarchicalNode.get_nodes_by_object(page)
    if len(nodes) > 0:
        children = nodes[0].get_children_objects(page)
    request = context['request']
    if 'current_page' in context:
        current_page = context['current_page']
        is_parent = HierarchicalNode.is_parent(page, current_page)
    return locals()

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
