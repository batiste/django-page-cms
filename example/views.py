from haystack.forms import FacetedSearchForm
from haystack.generic_views import FacetedSearchView, SearchView



class ExampleFacetedSearchView(FacetedSearchView):

    # form_class = FacetedSearchForm
    facet_fields = ['tags',]
    # template_name = 'search_result.html'
    paginate_by = 3
    context_object_name = 'object_list'