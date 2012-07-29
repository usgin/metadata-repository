from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.db.models import get_model
from metadatadb.proxy import proxyRequest
import json

ResourceCollection = get_model('registry', 'ResourceCollection')

def collection(req, collectionId):
    col = get_object_or_404(ResourceCollection, collection_id=collectionId)
    children = col.closure(req.user)
    return render_to_response('collection', locals(), context_instance=RequestContext(req))
    
def collection_resource(req, collectionId):
    col = get_object_or_404(ResourceCollection, collection_id=collectionId)
    collections = [{ 'id': col.collection_id, 'title': col.title, 'description': col.description, 'can_edit': col.can_edit(req.user) }]
    
    # Gather information about ALL editable collections for the add-to-collection dialog
    editable_cols = [ { 'id': col.collection_id, 'title': col.title } for col in ResourceCollection.objects.all() if col.can_edit(req.user) ]
    
    # Get a blank resource, add this collection to it
    #blank = proxyRequest('/metadata/schema/metadata/?emptyInstance=true', 'GET').content
    #blank = json.loads(blank)
    #blank['Collections'] = [ collectionId ]
    #blank = json.dumps(blank)
    
    # Construct template context and render
    context = {
        'jsonUpdate': json.dumps(False),
        #'jsonRecord':blank,
        #'record': json.loads(blank),
        'collections': json.dumps(collections),
        'update': False,         
        'allCollections': json.dumps(editable_cols)
    }
    return render_to_response('repository/edit.jade', context, context_instance=RequestContext(req))