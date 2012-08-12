from django.shortcuts import render_to_response
from django.template import RequestContext
from registry.models import ResourceCollection
from django.http import HttpResponse, HttpResponseBadRequest
import json

def browse(req):
    # Find all the collections that do not have parents
    top = ResourceCollection.objects.filter(parents__isnull=True)
    
    # Find the closure (all children) for each top-level collection
    result = [ col.jsonClosure(req.user) for col in top ]
    collections = json.dumps(result)
    return render_to_response('repository/browse.jade', {'collections': collections}, context_instance=RequestContext(req))

def populateCollection(req, collectionId):
    # Find this collection
    try:
        col = ResourceCollection.objects.get(collection_id=collectionId)
    except ResourceCollection.DoesNotExist:
        return HttpResponseBadRequest('There is no collection with the given ID: %s' % collectionId)
    
    # Find the children for this collection
    result = col.jsonClosure(req.user)
    collections = json.dumps(result)
    return HttpResponse(collections, content_type="application/json")
        
        