from django.http import HttpResponseNotAllowed, HttpResponse
from django.db.models import get_model
from metadatadb.proxy import proxyRequest
import json

Resource = get_model('registry', 'Resource')

def search(req): # Filter out unpublished? Tricky with the limit/skip and count parts of search results.
    if req.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    
    # Adjust the search to return ALL results, but record the limit and skip params
    search = json.loads(req.body)
    requestedLimit = search.get('limit', None)
    requestedSkip = search.get('skip', 0)
    try: del search['limit']
    except KeyError: pass
    try: del search['skip']
    except KeyError: pass
    
    # Perform a search that returns all the results
    fullSearch = json.dumps(search)    
    kwargs = {
        'path': '/metadata/search/',
        'method': req.method,
        'body': fullSearch,
        'headers': { 'Content-Type': 'application/json' }          
    }    
    fullResult = json.loads(proxyRequest(**kwargs).content)
    
    # Filter the full result set based on user permissions
    filteredResults = []
    for result in [ res['doc'] for res in fullResult['rows'] ]:
        try:
            res = Resource.objects.get(metadata_id=result['_id'])
            if res.can_view(req.user):
                filteredResults.append(result)
        except Resource.DoesNotExist:
            pass
        
    # Build the response, applying the original limit and skip parameters
    if requestedLimit: requestedLimit = requestedSkip + requestedLimit
    results = {
        'total_rows': len(filteredResults),
        'results': filteredResults[requestedSkip:requestedLimit],
        'skip': requestedSkip          
    }    
    
    return HttpResponse(json.dumps(results), content_type='application/json')