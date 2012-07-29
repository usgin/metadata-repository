from django.http import HttpResponseNotAllowed, HttpResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.db.models import get_model
from poster.encode import multipart_encode, MultipartParam
from poster.streaminghttp import register_openers
from metadatadb.proxy import proxyRequest, can_edit
from metadatadb.config import metadataServerUrl
import urllib2

Resource = get_model('registry', 'Resource')

def allFiles(req, resourceId):
    allowed = [ 'GET', 'POST' ] 
    if req.method not in allowed:
        return HttpResponseNotAllowed(allowed)
    
    def getFiles(req, resourceId):
        res = get_object_or_404(Resource, metadata_id=resourceId)
        if res.can_view(req.user):            
            kwargs = {
                'path': '/metadata/record/' + resourceId + '/file/',
                'method': req.method         
            }
            return proxyRequest(**kwargs)
        else:
            return HttpResponseForbidden('You cannot view this resource.')            
    
    @login_required # Registry tracking required?
    def newFile(req, resourceId):
        if not can_edit(req.user, resourceId): 
            return HttpResponseForbidden('You do not have permission to edit this resource')
        
        register_openers()
        theFile = req.FILES['upload-file']
        
        kwargs = {
            'name': 'upload-file',
            'filename': theFile.name,
            'filetype': theFile.content_type,
            'filesize': theFile.size,
            'fileobj': theFile          
        }
        params = MultipartParam(**kwargs)
        
        datagen, headers = multipart_encode([ params ])
        url = '/'.join([ metadataServerUrl, 'metadata/record', resourceId, 'file/' ])
        request = urllib2.Request(url, datagen, headers)
        response = urllib2.urlopen(request)
        
        clientResponse = HttpResponse()
        clientResponse.status_code = response.code
        clientResponse['Location'] = response.info()['Location']
        return clientResponse
    
    if req.method == 'GET': return getFiles(req, resourceId)
    if req.method == 'POST': return newFile(req, resourceId)