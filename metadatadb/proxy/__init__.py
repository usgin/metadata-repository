from django.http import HttpResponse, HttpResponseForbidden, Http404
from django.db.models import get_model
from metadatadb.config import metadataServerHost
from bs4 import BeautifulSoup
from lxml import etree
import httplib, json, re

Resource = get_model('registry', 'Resource')
ResourceCollection = get_model('registry', 'ResourceCollection')

def proxyRequest(path, method, body=None, headers=None):
    # HTTP Connection to the host
    conn = httplib.HTTPConnection(metadataServerHost)
    
    # Build request arguments
    kwargs = { "method": method, "url": path }
    if body != None: kwargs['body'] = body
    if headers != None: kwargs['headers'] = headers
    
    # Issue the request
    conn.request(**kwargs)
    response = conn.getresponse()
    
    # Build the client response
    res = HttpResponse()
    res.status_code = response.status
    res.content = response.read()
    contentType = response.getheader('Content-Type', None)
    contentLength = response.getheader('Content-Length', None)
    contentDisposition = response.getheader('Content-Disposition', None)
    location = response.getheader('Location', None)
    if contentType != None: res['Content-Type'] = contentType
    if contentLength != None: res['Content-Length'] = contentLength
    if contentDisposition != None: res['Content-Disposition'] = contentDisposition
    if location != None: res['Location'] = location
    
    # Send the client response
    return res

def can_edit(user, resourceId, resourceType='record'):
    if resourceType == 'record':
        try:
            res = Resource.objects.get(metadata_id=resourceId)
        except Resource.DoesNotExist:
            raise Http404
        
        # Check if the user has permissions to edit the resource
        if res.can_edit(user): return True
        return False
        
    elif resourceType == 'collection': 
        try:
            collection = ResourceCollection.objects.get(collection_id=resourceId)
        except ResourceCollection.DoesNotExist:
            raise Http404
        
        return collection.can_edit(user)
    
    else: return False

def hide_unpublished(user, response, view=None):
    # Each type of view has to be treated differently
    if view == 'iso.xml': return singleIso(user, response)
    elif view == 'atom.xml': return atom(user, response)
    elif view == 'geojson': return geojson(user, response)
    elif view == 'waf': return waf(user, response)
    # Otherwise we just deal with JSON data....
    
    # Parse the JSON data into Python objects
    content = json.loads(response.content)
    
    # Make sure we're dealing with a list for now
    if isinstance(content, list):
        returnList = True
    elif isinstance(content, dict):
        content = [ content ]
        returnList = False
    else: return content
    
    # Loop through the records in the list, appending to output as we go
    output = []
    for record in content:
        try:
            # Find out if the user can view the resource
            res = Resource.objects.get(metadata_id=record['id'])
            if res.can_view(user): output.append(record)
        except Resource.DoesNotExist:
            pass
    
    # Stringify the output    
    if returnList: output = json.dumps(output)
    elif len(output) == 0: output = ''
    else: output = json.dumps(output[0])
        
    # Adjust the HttpResponse and return it
    response['Content-Length'] = len(output)
    response.content = output
    return response

def singleIso(user, response):
    # Find the metadata ID
    match = re.search('<gmd:fileIdentifier><gco:CharacterString>(?P<id>.*)</gco:CharacterString></gmd:fileIdentifier>', response.content)
    resourceId = match.group('id')
    
    # Find the Resource
    try:
        res = Resource.objects.get(metadata_id=resourceId)
    except Resource.DoesNotExist:
        return response

    # If the user has edit permission, or in a group with edit permission, or its published, then they can see it
    if res.can_view(user): return response
    return HttpResponseForbidden('You do not have permission to view this resource')
    
def atom(user, response):
    root = etree.fromstring(response.content)
    for entry in root.xpath('//entry'):
        ids = [ ele.text for ele in entry if ele.tag == 'id' ]
        if len(ids) > 0:
            try:
                res = Resource.objects.get(metadata_id=ids[0])
                if not res.can_view(user): entry.getparent().remove(entry)
            except Resource.DoesNotExist: pass
    result = etree.tostring(root)          
    response['Content-Length'] = len(result)
    response.content = result
    return response

def geojson(user, response):
    original = json.loads(response.content)
    if original['type'] == 'FeatureCollection': records = original['features']
    else: records = [ original ]
    
    output = []
    for record in records:
        try:
            res = Resource.objects.get(metadata_id=record['id'])
            if res.can_view(user): output.append(record)
        except Resource.DoesNotExist:
            pass
    
    if original['type'] == 'FeatureCollection': original['features'] = output 
    else:
        if len(output) == 0: return HttpResponseForbidden('You do not have permission to view this resource')
        else: original = output[0]
        
    result = json.dumps(original)
    
    # Adjust the HttpResponse and return it
    response['Content-Length'] = len(result)
    response.content = result
    return response
        
def waf (user, response):
    soup = BeautifulSoup(response.content)
    for li in soup.find_all('li'):
        resourceId = li.a.string.rstrip('.xml')
        li.a['href'] = '/metadata' + li.a['href']
        try:
            res = Resource.objects.get(metadata_id=resourceId)
            if not res.can_view(user): li.extract()
        except Resource.DoesNotExist:
            pass
    result = str(soup)
    
    # Adjust the HttpResponse and return it
    response['Content-Length'] = len(result)
    response.content = result
    return response
    

from search import search
from allResources import allResources
from viewRecords import viewRecords
from harvestRecord import harvestRecord
from oneResource import oneResource
from viewRecord import viewRecord
from getCollectionRecords import getCollectionRecords
from viewCollectionRecords import viewCollectionRecords
from allFiles import allFiles
from oneFile import oneFile
from schemas import allSchemas, oneSchema
from sync import delUnpublish