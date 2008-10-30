from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect

from pages import settings

def auto_render(func):
    """Decorator that put automaticaly the template path in the context dictionary
    and call the render_to_response shortcut"""
    def _dec(request, *args, **kwargs):
        t = None
        
        if kwargs.get('only_context', False):
            # return only context dictionary
            del(kwargs['only_context'])
            response = func(request, *args, **kwargs)
            if isinstance(response, HttpResponse) or isinstance(response, HttpResponseRedirect):
                raise Except("cannot return context dictionary because a HttpResponseRedirect as been found")
            (template_name, context) = response
            return context
        
        if "template_name" in kwargs:
            t = kwargs['template_name']
            del kwargs['template_name']
        response = func(request, *args, **kwargs)
        if isinstance(response, HttpResponse) or isinstance(response, HttpResponseRedirect):
            return response
        (template_name, context) = response
        if not t:
            t = template_name
        context['template_name'] = t
        return render_to_response(t, context, context_instance=RequestContext(request))
    return _dec

def get_template_from_request(request, obj=None):
    """
    Gets a valid template from different sources or falls back to the default
    template.
    """
    template = request.REQUEST.get('template', None)
    if template is not None and \
            template in dict(settings.PAGE_TEMPLATES).keys():
        return template
    if obj:
        return obj.get_template()
    return settings.DEFAULT_PAGE_TEMPLATE
