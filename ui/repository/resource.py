from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseForbidden
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.db.models import get_model
from django.shortcuts import get_object_or_404
from metadatadb.proxy import proxyRequest
import json, datetime

Resource = get_model('registry', 'Resource')
ResourceCollection = get_model('registry', 'ResourceCollection')

def get_metadata(resource):
    return proxyRequest('/metadata/record/%s/' % resource.metadata_id, 'GET').content
    
def resource(req, resourceId):
    res = get_object_or_404(Resource, metadata_id=resourceId)
    if not res.can_view(req.user):
        return HttpResponseForbidden()
    
    # Get the record itself
    record = json.loads(get_metadata(res))
    
    # Gather information about the collections the record belongs to
    collections = []
    for collectionId in record['Collections']:
        try:
            col = ResourceCollection.objects.get(collection_id=collectionId)
            collections.append(col)
        except ResourceCollection.DoesNotExist: pass
        
    # Gather information about the online availabilty of the resource
    #  This includes those things refered to in the metadata.links...
    service_types = { "OGC:WMS": "WMS Capabilities", "OGC:WFS": "WFS Capabilities", "OGC_WCS": "WCS Capabilities", "ESRI": "ESRI Service Endpoint", "OPENDAP": "OPeNDap Service" };
    def build_link(link):
        if 'Name' in link.keys() and link['Name'] != '' and link['Name'] != None:
            label = link['Name']
        elif 'ServiceType' in link.keys() and link['ServiceType'] in service_types.keys():
            label = service_types[link['ServiceType']]
        elif 'ServiceType'in link.keys():
            label = 'Web Service'
        else:
            label = 'Downloadable File'
        return { 'url': link['URL'], 'label': label }
    links = [ build_link(l) for l in record['Links'] ]        
    
    # List Author Names
    def getName(author):
        if 'OrganizationName' in author.keys():
            if 'Name' in author.keys():
                if author['Name'] == 'No Name Was Given': return author['OrganizationName']
                else: return author['Name']
            else:
                return author['OrganizationName']            
        else: return author['Name']
    author_names = [ getName(author) for author in record['Authors'] ]
    
    #Stringify the Publication Date
    try:
        pubDate = datetime.datetime.strptime(record['PublicationDate'], '%Y-%m-%dT%H:%M:%S')
    except ValueError:
        pubDate = datetime.datetime.strptime(record['PublicationDate'], '%Y-%m-%dT%H:%M:%SZ')
    pub_date = pubDate.strftime('%b %d, %Y')
    
    # Build render context for the page
    context = {
        'record': record,
        'collections': collections,
        'links': links,
        'can_edit': res.can_edit(req.user),
        'author_names': ', '.join(author_names),
        'pub_date': pub_date         
    }
    
    # Render the page
    return render_to_response('repository/resource.jade', context, context_instance=RequestContext(req))

def edit_responder(req, resourceId=None):
    allowed_methods = ['GET', 'POST']
    if req.method not in allowed_methods:
        return HttpResponseNotAllowed(allowed_methods)
    
    # Gather information about ALL editable collections for the add-to-collection dialog
    editable_cols = [ { 'id': col.collection_id, 'title': col.title } for col in ResourceCollection.objects.all() if col.can_edit(req.user) ]
            
    if req.method == 'GET':
        if resourceId:
            res = get_object_or_404(Resource, metadata_id=resourceId)
            if not res.can_edit(req.user):
                return HttpResponseForbidden()
            
            # Get the record itself
            record = json.loads(get_metadata(res))
            
            # Gather information about the collections the record belongs to
            collections = []
            for collectionId in record['Collections']:
                try:
                    col = ResourceCollection.objects.get(collection_id=collectionId)
                    collections.append({ 'id': col.collection_id, 'title': col.title, 'description': col.description, 'can_edit': col.can_edit(req.user) })
                except ResourceCollection.DoesNotExist: pass                    
                            
            context = {
                'jsonUpdate': json.dumps(True),
                'update': True,            
                'jsonRecord': get_metadata(res),
                'record': json.loads(get_metadata(res)),
                'collections': json.dumps(collections),
                'allCollections': json.dumps(editable_cols)
            }
        else:
            context = {
                'jsonUpdate': json.dumps(False),
                'update': False,         
                'allCollections': json.dumps(editable_cols)
            }
        return render_to_response('repository/edit.jade', context, context_instance=RequestContext(req))
    elif req.method == 'POST':
        return HttpResponse('Not Quite Yet!!')
    
def edit(req, resourceId):
    # Block the page from user's without appropriate permission
    res = get_object_or_404(Resource, metadata_id=resourceId)
    if not res.can_edit(req.user):
        return HttpResponseNotAllowed()
    
    # Render the page
    return edit_responder(req, resourceId)
    
def new(req):
    return edit_responder(req)
    
    
    