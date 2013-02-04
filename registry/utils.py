from django.http import HttpResponse
from django.contrib.auth.decorators import permission_required
from metadatadb.proxy import proxyRequest
from models import Resource, ResourceCollection, Contact
import json

def sync():
    # Purge existing data
    Resource.objects.all().delete()
    ResourceCollection.objects.all().delete()
    Contact.objects.all().delete()
    
    # Retrieve all the metadata collections from CouchDB
    collectionResponse = proxyRequest('/metadata/collection/', 'GET')
    collections = json.loads(collectionResponse.content)
    
    # Create a ResourceCollection for each one
    for collection in collections:
        try:
            col = ResourceCollection.objects.get(collection_id=collection['id'])
            col.title = collection['Title']
            col.description = collection.get('Description','')
            col.save()
        except ResourceCollection.DoesNotExist:
            col = ResourceCollection.objects.create(collection_id=collection['id'], title=collection['Title'], description=collection.get('Description',''))
        
    # Add parent collections, needs to be done in a separate loop so that all parents are already in place
    for collection in collections:
        col = ResourceCollection.objects.get(collection_id=collection['id'])
        for parentId in collection.get('ParentCollections', []):
            try:                            
                par = ResourceCollection.objects.get(collection_id=parentId)
                col.parents.add(par)
            except ResourceCollection.DoesNotExist:
                pass
            
    # Retrieve all the metadata records from CouchDB
    recordResponse = proxyRequest('/metadata/record/', 'GET')
    records = json.loads(recordResponse.content)
    
    # Create a Resource for each one
    for record in records:
        try:
            res = Resource.objects.get(metadata_id=record['id'])
            res.title = record['Title']
            res.published = record['Published']
            res.save()
        except Resource.DoesNotExist:
            res = Resource.objects.create(metadata_id=record['id'], title=record['Title'], published=record.get('Published', False))
    
        # Add the Resource to the appropriate ResourceCollections
        for collection_id in record.get('Collections', []):
            try: 
                col = ResourceCollection.objects.get(collection_id=collection_id)
                res.collections.add(col)
            except ResourceCollection.DoesNotExist:
                pass
        
        # Contact tracking
        contacts = record['Authors'] + record['Distributors']
        for contact in contacts:
            personName = contact.get('Name', 'No Name Was Given')
            orgName = contact.get('OrganizationName', 'No Name Was Given')
            if personName in [ 'No Name Was Given', '' ]: name = orgName
            else: name = personName
                               
            try:
                Contact.objects.get(name=name)
            except Contact.DoesNotExist:
                Contact.objects.create(name=name, json=json.dumps(contact))

@permission_required('registry.edit_any_resource')            
def synch_to_couchdb(req):
    sync()
    return HttpResponse('Success')

def add_to_collections(input_collection_id, output_collections, publish=True):
    """
    input_collection_id is an existing collection. Each resource in that collection will
    be moved into all the output_collections, and optionally published
    """
    resources = ResourceCollection.objects.get(collection_id=input_collection_id).resource_set.all()
    new_collections = [ ResourceCollection.objects.get(collection_id=col_id) for col_id in output_collections ]
    for resource in resources:
        for collection in new_collections:
            resource.collections.add(collection)
        if publish:
            resource.published = True
    
     