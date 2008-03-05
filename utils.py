from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect

def auto_render(func):
    """Decorator that put automaticaly the template path in the context dictionary
    and call the render_to_response shortcut"""
    def _dec(request, *args, **kwargs):
        response = func(request, *args, **kwargs)
        if isinstance(response, HttpResponse) or isinstance(response, HttpResponseRedirect):
            return response
        (template_name, context) = response
        context['template_name'] = template_name
        return render_to_response(template_name, context, context_instance=RequestContext(request))
    return _dec