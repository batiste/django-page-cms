from django import template
from ..pages.models import Language, Content
register = template.Library()

@register.inclusion_tag('menu.html')
def show_menu(page, url='/'):
    children = page.children.filter(status=1)
    return locals()

@register.inclusion_tag('admin_menu.html')
def show_admin_menu(page, url='/admin/pages/page/'):
    children = page.children.all()
    return locals()

@register.inclusion_tag('content.html')
def show_content(page, content_type, request):
    l = Language.get_from_request(request)
    code = None
    for ct in Content.CONTENT_TYPE:
        if ct[1] == content_type:
            code = ct[0]
            break
    if code is not None:
        c = Content.get_content(page, l, code, True)
        if c:
            return {'content':c}
    else:
        return {'content':''}