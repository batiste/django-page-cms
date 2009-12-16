from django.shortcuts import render_to_response
from django.template import loader, Context, RequestContext
from example.documents.models import Document

def document_view(request, **kwargs):
    context = RequestContext(request, kwargs)
    documents = Document.objects.filter(page=kwargs['current_page'])
    context['documents'] = documents
    if kwargs.has_key('document_id'):
        document = Document.objects.get(pk=int(kwargs['document_id']))
        context['document'] = document
    context['in_document_view'] = True
    return render_to_response('pages/index.html', context)
