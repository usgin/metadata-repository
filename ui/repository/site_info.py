from django.http import HttpResponse
from django.shortcuts import render_to_response
from subprocess import check_call, CalledProcessError
from django.template import RequestContext
import json, httplib

def contact(req):
    return HttpResponse('Not Implemented Yet', status=501)

def about(req):
    context = RequestContext(req)
    return render_to_response('repository/about.jade', context_instance=context)

def terms(req):
    context = RequestContext(req)
    return render_to_response('repository/terms.jade', context_instance=context)

def rant(req):
    return HttpResponse('Not Implemented Yet', status=501)

def invalid_urls(req):
    if req.GET.get('refresh', False):
        code = refresh_invalid_urls()
        return HttpResponse(json.dumps({'returncode':code}), mimetype='application/json')
                            
    url = '/records/_design/manage/_view/invalidUrls'
    conn = httplib.HTTPConnection('localhost:5984')    
    conn.request(method='GET', url=url)
    response = conn.getresponse()
    content = response.read()    
    return render_to_response('repository/invalidUrls.jade', json.loads(content))

def refresh_invalid_urls():
    try:
        return check_call(['/usr/local/bin/node', 'flagInvalidUrls.js'], cwd='/Users/ryan/dev/metadata-server/build/helpers')
    except CalledProcessError as err:
        return err.returncode