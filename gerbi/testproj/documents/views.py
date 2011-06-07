from django.template import RequestContext
from gerbi.testproj.documents.models import Document
from gerbi.http import auto_render

def document_view(request, *args, **kwargs):
    context = RequestContext(request, kwargs)
    if kwargs.get('current_page', False):
        documents = Document.objects.filter(page=kwargs['current_page'])
        context['documents'] = documents
    if kwargs.has_key('document_id'):
        document = Document.objects.get(pk=int(kwargs['document_id']))
        context['document'] = document
    context['in_document_view'] = True
    return 'gerbi/examples/index.html', context

document_view = auto_render(document_view)
