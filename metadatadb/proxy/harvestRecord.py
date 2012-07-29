from django.http import HttpResponseNotAllowed
from django.contrib.auth.decorators import login_required
from metadatadb.proxy import proxyRequest
from registry.tracking import track_resource
import json

@login_required
def harvestRecord(req):
    if req.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    
    kwargs = {
        'path': '/metadata/harvest/',
        'method': req.method,
        'body': req.body,
        'headers': { 'Content-Type': 'application/json' }          
    }
    response = proxyRequest(**kwargs)
    if response.status_code == 200:
        # Track the newly created resources
        content = json.loads(response.content)
        for res in content:
            loc = res.strip('/').split('/')
            kwargs = {
                'user': req.user,
                'resourceId': loc.pop(),
                'content': json.loads(proxyRequest(res, 'GET').content)          
            }
            track_resource(**kwargs)
    return response