from django.http import HttpResponse
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
            
def synch_to_couchdb(req):
    sync()
    return HttpResponse('Success')