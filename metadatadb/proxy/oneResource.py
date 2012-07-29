from django.http import HttpResponseNotAllowed, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from metadatadb.proxy import proxyRequest, can_edit, hide_unpublished
from registry.tracking import track_resource
import json

def oneResource(req, resourceType, resourceId):
    allowed = [ 'GET', 'PUT', 'DELETE' ]
    if req.method not in allowed:
        return HttpResponseNotAllowed(allowed)
    
    def getResource(req, resourceType, resourceId):
        kwargs = {
            'path': '/metadata/' + resourceType + '/' + resourceId + '/',
            'method': req.method         
        }
        if resourceType == 'record':
            response = hide_unpublished(req.user, proxyRequest(**kwargs))
            if response.content == '':
                return HttpResponseForbidden('You do not have permission to view this resource')
            return response            
        else:
            return proxyRequest(**kwargs)
        
    @login_required  
    def updateResource(req, resourceType, resourceId):
        if not can_edit(req.user, resourceId, resourceType): 
            return HttpResponseForbidden('You do not have permission to edit this resource')
        
        kwargs = {
            'path': '/metadata/' + resourceType + '/' + resourceId + '/',
            'method': req.method,
            'body': req.body,
            'headers': { 'Content-Type': 'application/json' }          
        }
        response = proxyRequest(**kwargs)
        if response.status_code == 204:
            kwargs = {
                'user': req.user,
                'resourceId': resourceId,
                'content': json.loads(req.body),
                'resourceType': resourceType          
            }
            track_resource(**kwargs)
        return response
    
    @login_required
    def deleteResource(req, resourceType, resourceId):
        if not can_edit(req.user, resourceId, resourceType): 
            return HttpResponseForbidden('You do not have permission to edit this resource')
        
        kwargs = {
            'path': '/metadata/' + resourceType + '/' + resourceId + '/',
            'method': req.method         
        }
        original = proxyRequest(kwargs['path'], 'GET')
        if original.status_code == 200: content = json.loads(original.content)        
        response = proxyRequest(**kwargs)
        if response.status_code == 204:
            kwargs = {
                'user': req.user,
                'resourceId': resourceId,
                'content': content,
                'resourceType': resourceType,
                'isDelete': True        
            }
            track_resource(**kwargs)
        return response

    if req.method == 'GET': return getResource(req, resourceType, resourceId)
    if req.method == 'PUT': return updateResource(req, resourceType, resourceId)
    if req.method == 'DELETE': return deleteResource(req, resourceType, resourceId)