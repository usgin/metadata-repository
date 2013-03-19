from django.http import HttpResponse, HttpResponseNotAllowed
from django.db.models import get_model
from metadatadb.proxy import proxyRequest


Resource = get_model('registry', 'Resource')

def delUnpublish(req):
       
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
            numDelCouch += 1
            if res.status_code != 204:
                return res
            
        unpub.delete()
        numDelDjango += 1    
     
    return HttpResponse("Delete " + str(numDelDjango) + " unpublished records in PostgreSQL & " + str(numDelCouch) + " unpublished records in CouchDB")
                 
        
    