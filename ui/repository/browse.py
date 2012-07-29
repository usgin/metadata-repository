from django.shortcuts import render_to_response
from django.template import RequestContext
from registry.models import ResourceCollection
import json

def browse(req):
    # Find all the collections that do not have parents
    top = ResourceCollection.objects.filter(parents__isnull=True)
    
    # Find the closure (all children) for each top-level collection
    result = [ col.jsonClosure(req.user) for col in top ]
    return render_to_response('repository/browse.jade', {'collections': json.dumps(result)}, context_instance=RequestContext(req))