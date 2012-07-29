from django.http import HttpResponseNotAllowed, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from metadatadb.proxy import proxyRequest, can_edit, hide_unpublished

def oneFile(req, resourceId, fileName):
    allowed = [ 'GET', 'DELETE' ]
    if req.method not in allowed:
        return HttpResponseNotAllowed(allowed)   
    
    def getFile(req, resourceId, fileName):        
        response = hide_unpublished(req.user, proxyRequest(path='/metadata/record/' + resourceId + '/', method='GET'))
        if response.content == '':
            return HttpResponseForbidden('You do not have permission to view this resource')
        else:
            kwargs = {
                'path': '/metadata/record/' + resourceId + '/file/' + fileName,
                'method': req.method         
            }            
            return proxyRequest(**kwargs)
    
    @login_required # Registry tracking required?
    def deleteFile(req, resourceId, fileName):
        if not can_edit(req.user, resourceId): 
            return HttpResponseForbidden('You do not have permission to edit this resource')
        
        kwargs = {
            'path': '/metadata/record/' + resourceId + '/file/' + fileName,
            'method': req.method         
        }
        return proxyRequest(**kwargs)

    if req.method == 'GET': return getFile(req, resourceId, fileName)
    if req.method == 'DELETE': return deleteFile(req, resourceId, fileName)