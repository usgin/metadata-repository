from django.http import HttpResponseNotAllowed
from django.contrib.auth.decorators import login_required
from metadatadb.proxy import proxyRequest, hide_unpublished
from registry.tracking import track_resource
import json

def allResources(req, resourceType):
    allowed = [ 'GET', 'POST' ]
    if req.method not in allowed:
        return HttpResponseNotAllowed(allowed)
    
    def getResources(req, resourceType):
        kwargs = {
            'path': '/metadata/' + resourceType + '/',
            'method': req.method         
        }
        if resourceType == 'record':
            return hide_unpublished(req.user, proxyRequest(**kwargs))
        else: return proxyRequest(**kwargs)
    
    @login_required
    def newResource(req, resourceType):
        body = json.loads(req.body)
        body['MetadataContact'] = req.user.get_profile().to_contact()
        
        kwargs = {
            'path': '/metadata/' + resourceType + '/',
            'method': req.method,
            'body': json.dumps(body),
            'headers': { 'Content-Type': 'application/json' }          
        }
        response = proxyRequest(**kwargs)
        if response.status_code == 201:
            loc = response['Location'].strip('/').split('/')
            kwargs = {
                'user': req.user,
                'resourceId': loc.pop(),
                'content': json.loads(req.body),
                'resourceType': resourceType          
            }
            track_resource(**kwargs)
        return response
    
    if req.method == 'GET': return getResources(req, resourceType)
    if req.method == 'POST': return newResource(req, resourceType)