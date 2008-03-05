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
    return locals()

@register.inclusion_tag('pages/content.html', takes_context=True)
def show_content(context, page, content_type):
    l = Language.get_from_request(context['request'])
    request = context['request']
    code = Page.get_status_code(content_type)
    if code is not None:
        c = Content.get_content(page, l, code, True)
        if c:
            return {'content':c}
    else:
        return {'content':''}