from django.shortcuts import render_to_response
from django.template import RequestContext
from django.db.models import get_model
import json

ResourceCollection = get_model('registry', 'ResourceCollection')

def harvest(req):
    class Format():
        key = ''
        label = ''        
        def __init__(self, key, label):
            self.key = key
            self.label = label
    collections = [ { 'id': col.collection_id, 'value': col.title } for col in [ rs for rs in ResourceCollection.objects.all() if rs.can_edit(req.user) ] ]        
    context = { 'formats': [ Format('iso.xml', 'USGIN ISO 19139'), Format('atom.xml', 'Atom Feed'), Format('fgdc.xml', 'FGDC'), Format('csv', 'CSV') ], 'collections': json.dumps(collections) }
    return render_to_response('repository/harvest.jade', context, context_instance=RequestContext(req))