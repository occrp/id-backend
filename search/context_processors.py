from search.models import SEARCH_TYPES

def search_types(request):
    return {
        'search_types': SEARCH_TYPES,
    }
