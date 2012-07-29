from django.http import HttpResponseNotAllowed
from metadatadb.proxy import proxyRequest, hide_unpublished

def viewRecord(req, resourceId, viewFormat):
    if req.method != 'GET':
        return HttpResponseNotAllowed(['GET'])
    
    kwargs = {
        'path': '/metadata/record/' + resourceId + '.' + viewFormat,
        'method': req.method         
    }
    return hide_unpublished(req.user, proxyRequest(**kwargs), viewFormat)