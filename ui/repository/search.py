from django.shortcuts import render_to_response
from django.template import RequestContext
import json

def search(req, term=None):
    return render_to_response('repository/search.jade', { 'term': json.dumps(term) }, context_instance=RequestContext(req))