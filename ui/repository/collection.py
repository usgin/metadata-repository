from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.db.models import get_model
from metadatadb.proxy import proxyRequest
import json

ResourceCollection = get_model('registry', 'ResourceCollection')

def collection(req, collectionId):
    col = get_object_or_404(ResourceCollection, collection_id=collectionId)
    
    # Find the closure (all children) for this collection
    result = [ col.jsonClosure(req.user) ]
    return render_to_response('repository/browse.jade', {'collections': json.dumps(result)}, context_instance=RequestContext(req))
    
def collection_resource(req, collectionId):
    col = get_object_or_404(ResourceCollection, collection_id=collectionId)
    collections = [{ 'id': col.collection_id, 'title': col.title, 'description': col.description, 'can_edit': col.can_edit(req.user) }]
    
    # Gather information about ALL editable collections for the add-to-collection dialog
    editable_cols = [ { 'id': col.collection_id, 'title': col.title } for col in ResourceCollection.objects.all() if col.can_edit(req.user) ]
    
    # Construct template context and render
    context = {
        'jsonUpdate': json.dumps(False),
        'collections': json.dumps(collections),
        'update': False,         
        'allCollections': json.dumps(editable_cols)
    }
    return render_to_response('repository/edit.jade', context, context_instance=RequestContext(req))