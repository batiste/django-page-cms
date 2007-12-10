from django import template
from ..pages.models import Language, Content
register = template.Library()

@register.inclusion_tag('menu.html', takes_context=True)
def show_menu(context, page, url='/'):
    children = page.children.filter(status=1)
    request = context['request']
    return locals()

@register.inclusion_tag('admin_menu.html', takes_context=True)
def show_admin_menu(context, page, url='/admin/pages/page/'):
    children = page.children.all()
    request = context['request']
    return locals()

@register.inclusion_tag('content.html', takes_context=True)
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