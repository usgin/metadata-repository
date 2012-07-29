from django.http import HttpResponseNotAllowed
from metadatadb.proxy import proxyRequest
import urllib

def allSchemas(req):
    allowed = [ 'GET' ]
    if req.method not in allowed:
        return HttpResponseNotAllowed(allowed)
    
    kwargs = {
        'path': '/metadata/schema/',
        'method': req.method         
    } 
    return proxyRequest(**kwargs)

def oneSchema(req, schemaId):
    allowed = [ 'GET' ]
    if req.method not in allowed:
        return HttpResponseNotAllowed(allowed)
    
    path = '/metadata/schema/' + urllib.quote_plus(schemaId.encode("utf-8")) + '/'
    if req.GET.get('resolve', False):
        path = '%s?resolve=%s' % (path, req.GET.get('resolve'))
    if req.GET.get('emptyInstance', False):
        path = '%s?emptyInstance=%s' % (path, req.GET.get('emptyInstance'))
    
    kwargs = {
        'path': path,
        'method': req.method         
    }
    return proxyRequest(**kwargs)