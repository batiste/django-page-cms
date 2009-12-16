from django.shortcuts import render_to_response
from django.template import loader, Context, RequestContext

def blog(request, **kwargs):
    context = RequestContext(request, kwargs)
    context['in_blog_view'] = True
    return render_to_response('pages/index.html', context)