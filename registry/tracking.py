from django.db.models import get_model
import json

Resource = get_model('registry', 'Resource')
ResourceCollection = get_model('registry', 'ResourceCollection')
Contact = get_model('registry', 'Contact')

def track_resource(user, resourceId, content, resourceType='record', isDelete=False):
    if resourceType == 'record': track_record(user, resourceId, content, isDelete)
    elif resourceType == 'collection': track_collection(user, resourceId, content, isDelete)
    else: return
    
def track_record(user, resourceId, content, isDelete):
    try:
        res = Resource.objects.get(metadata_id=resourceId)        
    except Resource.DoesNotExist:
        res = Resource.objects.create(metadata_id=resourceId)
        res.editors.add(user)
    
    # Basic record information    
    res.title = content['Title']
    res.published = content['Published']
    res.save()
    
    # Collections Information
    res.collections.clear()
    for collectionId in content['Collections']:
        try:
            col = ResourceCollection.objects.get(collection_id=collectionId)
            res.collections.add(col)
        except ResourceCollection.DoesNotExist:
            pass
    
    # Contact tracking
    contacts = content['Authors'] + content['Distributors']
    for contact in contacts:
        if ('Name' not in contact.keys() or contact['Name'] == 'No Name Was Given' or contact['Name'] == '') and 'OrganizationName' in contact.keys():
            name = contact['OrganizationName']
        else: name = contact['Name']
        try:
            Contact.objects.get(name=name)
        except Contact.DoesNotExist:
            Contact.objects.create(name=name, json=json.dumps(contact))
            
    if isDelete: res.delete()
        
def track_collection(user, resourceId, content, isDelete):
    try:
        col = ResourceCollection.objects.get(collection_id=resourceId)
    except ResourceCollection.DoesNotExist:
        col = ResourceCollection.objects.create(collection_id=resourceId)
        col.editors.add(user)
        
    col.title = content['Title']
    col.description = content.get('Description','')
    col.parents.clear()
    for collectionId in content.get('ParentCollections', []):
        try:
            par = ResourceCollection.objects.get(collection_id=collectionId)
            col.parents.add(par)
        except ResourceCollection.DoesNotExist:
            pass
    if isDelete: col.delete()
    else: col.save()
