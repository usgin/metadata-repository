from django.http import HttpResponse, HttpResponseNotAllowed
from django.db.models import get_model
from metadatadb.proxy import proxyRequest
import json

Resource = get_model('registry', 'Resource')


def delUnpublish(req):
    """
    Delete unpublished records in Django Postgresql and their related records in CouchDB
    If the records exist in CouchDB, not in Django, please use delCouchExtraRec function
    """       
    allowed = [ 'DELETE'] 
    if req.method not in allowed:
        return HttpResponseNotAllowed(allowed)
    
    numDelDjango = 0
    numDelCouch = 0
    
    unpubSet = Resource.objects.filter(published=False)
    
    for unpub in unpubSet:
        kwargs = {
            'path': '/metadata/record/' + str(unpub.metadata_id) + '/',
            'method': 'GET'         
        }
       
        res = proxyRequest(**kwargs)       
        if res.status_code == 200:
            kwargs = {
                'path': '/metadata/record/' + str(unpub.metadata_id) + '/',
                'method': 'DELETE'         
            }
            res = proxyRequest(**kwargs)
            
            if res.status_code == 204:
                numDelCouch += 1
            else:
                return res
            
        unpub.delete()
        numDelDjango += 1    
     
    return HttpResponse("Delete " + str(numDelDjango) + " unpublished records in PostgreSQL & " + str(numDelCouch) + " unpublished records in CouchDB")

def delCouchExtraRec(req):
    """
    Delete the records wheich only exist in CouchDB
    """     
    
    numDelCouch = 0 
       
    allowed = [ 'DELETE'] 
    if req.method not in allowed:
        return HttpResponseNotAllowed(allowed)
    
    kwargs = {
        'path': '/metadata/record/',
        'method': 'GET'         
    }
    res = proxyRequest(**kwargs)
    if res.status_code == 200:
        resList = json.loads(res.content)
        for r in resList:
            if Resource.objects.filter(metadata_id=r['id']).count() == 0:
                kwargs = {
                    'path': '/metadata/record/' + str(r['id']) + '/',
                    'method': 'DELETE'         
                }
                res = proxyRequest(**kwargs)
                
                if res.status_code == 204:
                    numDelCouch += 1
                else:
                    return res               
    return HttpResponse("Delete " + str(numDelCouch) + " CouchDB records, which do not exist in Django!")
    