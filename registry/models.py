from django.db import models
from django.contrib.auth.models import User

class Resource(models.Model):
    class Meta:
        permissions = (
            ('edit_any_resource', 'Can edit any metadata records'),               
        )
        ordering = ['title']
    
    metadata_id = models.CharField(max_length=50)
    title = models.CharField(max_length=500, blank=True)
    published = models.BooleanField()
    gis_file_location = models.CharField(max_length=50, blank=True)
    wfs_feature_id = models.CharField(max_length=50, blank=True)
    wms_layer_id = models.CharField(max_length=50, blank=True)
    editors = models.ManyToManyField(User)
    collections = models.ManyToManyField('ResourceCollection', null=True)
    
    def __unicode__(self):
        if self.title != '': return self.title
        else: return 'Untitled Resource: ' + self.id
        
    def can_edit(self, user):
        if user.has_perm('registry.edit_any_resource') or user in self.editors.all():
            return True
        for col in self.collections.all():
            if col.can_edit(user): return True
        return False
    
    def can_view(self, user):
        if self.can_edit(user): return True
        if self.published: return True
        return False
    
    def metadata_link(self):
        return '<a href="/metadata/record/' + self.metadata_id + '.iso.xml">View metadata</a>'
    metadata_link.allow_tags = True        
    
    def file_names(self):
        return []
        
class ResourceCollection(models.Model):
    class Meta:
        permissions = (
            ('edit_any_resource_collection', 'Can edit any metadata records'),               
        )
        ordering = ['title']
    
    collection_id = models.CharField(max_length=50)
    title = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    editors = models.ManyToManyField(User)
    parents = models.ManyToManyField('self', symmetrical=False, null=True)
    
    def __unicode__(self):
        if self.title != '': return self.title
        else: return 'Untitled ResourceCollection: ' + self.id
        
    def can_edit(self, user):
        if user.has_perm('registry.edit_any_resource_collection') or user in self.editors.all():
            return True
        return False
    
    # Return child collections
    def children(self):
        return ResourceCollection.objects.filter(parents__in=[self])
    
    # Recursive function returns an object with the full closure of child objects - collections and records
    #  Results are filtered by user permissions
    def closure(self, user):
        class Closure():
            collections = list()
            records = list()
            
            def __init__(self, collection, user):
                self.this = collection
                self.can_edit = collection.can_edit(user)
            
        result = Closure(self, user)
        result.collections = [ child.closure(user) for child in self.children() ]
        result.records = [ resource for resource in self.resource_set.all() if resource.can_view(user) ]
        
        return result
    
    # Same as above, but returns an object that can be serialized into JSON string with json.dumps
    def jsonClosure(self, user):
        child_collections = [ child.oneLevelJsonClosure(user) for child in self.children() ]        
        
        # Setup for determining permissions as efficiently as possible
        can_edit = False        
        all_resources = self.resource_set.all().prefetch_related('editors')
        # First determine if the user is administrator or not
        if user.has_perm('registry.edit_any_resource'):            
            can_edit = True
        # Not admin, but are they a collection editor? If so they can edit any resource in the collection
        else:
            collection_editors = self.editors.all().values_list('pk', flat=True)
            can_edit = user.has_perm('registry.edit_any_resource_collection') or user.pk in collection_editors
        # Now check if they have edit permissions at this point. If not, we have check if they can view        
        if can_edit:
            viewable_resources = all_resources        
        else:
            viewable_resources = [ res for res in all_resources if user.pk in res.editors.values_list('pk', flat=True) or res.published ]                        
        # Build the JSON object that need to be sent to the client
        viewable_resources = [ {'title':res.title,'id':res.metadata_id, 'can_edit': can_edit} for res in viewable_resources]
        # Put it all together
        result = {
            'title': self.title,
            'description': self.description,
            'id': self.collection_id,
            'can_edit': can_edit,            
            'child_collections': child_collections,
            'child_resources': viewable_resources                
        }                
        # And return it
        return result
    
    # Don't return any of the children    
    def oneLevelJsonClosure(self, user):
        result = {
            'title': self.title,
            'description': self.description,
            'id': self.collection_id,
            'can_edit': self.can_edit(user),
            'child_collections': [],
            'child_resources': []        
        }
        return result
    
class Contact(models.Model):
    class Meta:
        ordering = ['name']
        
    name = models.CharField(max_length=500)
    json = models.TextField()
        
    def __unicode__(self):
        return self.name