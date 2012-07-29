from django.http import HttpResponseNotAllowed
from metadatadb.proxy import proxyRequest, hide_unpublished
    
def getCollectionRecords(req, resourceId):
    if req.method != 'GET':
        return HttpResponseNotAllowed(['GET'])
    
    kwargs = {
        'path': '/metadata/collection/' + resourceId + '/records/',
        'method': req.method         
    }
    dbResponse = proxyRequest(**kwargs)
    if dbResponse.status_code == 200:
        return hide_unpublished(req.user, proxyRequest(**kwargs))
    else: return dbResponse