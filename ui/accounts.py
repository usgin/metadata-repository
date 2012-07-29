from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext

def profile(req):
    return render_to_response('accounts/profile.jade', { 'user': req.user }, context_instance=RequestContext(req))

def register(req):
    return HttpResponse('Not Implemented Yet', status=501)