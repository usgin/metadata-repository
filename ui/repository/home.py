from django.shortcuts import render_to_response
from django.template import RequestContext

def home(req):
    context = RequestContext(req)
    return render_to_response('repository/home.jade', context_instance=context)