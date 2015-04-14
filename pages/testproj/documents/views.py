from django.template import RequestContext
from django.shortcuts import render_to_response
from pages.testproj.documents.models import Document

def document_view(request, *args, **kwargs):
    context = kwargs
    if kwargs.get('current_page', False):
        documents = Document.objects.filter(page=kwargs['current_page'])
        context['documents'] = documents
    if 'document_id' in kwargs:
        document = Document.objects.get(pk=int(kwargs['document_id']))
        context['document'] = document
    context['in_document_view'] = True
    rcontext = RequestContext(request, context)

    return render_to_response('pages/examples/index.html', 
        rcontext)
