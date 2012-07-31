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
        result = {
            'title': self.title,
            'description': self.description,
            'id': self.collection_id,
            'can_edit': self.can_edit(user),
            'child_collections': [ child.jsonClosure(user) for child in self.children() ],
            'child_resources': [ { 'title': resource.title, 'id': resource.metadata_id, 'can_edit': resource.can_edit(user) } for resource in self.resource_set.all() if resource.can_view(user) ]        
        }
        return result

class Contact(models.Model):
    class Meta:
        ordering = ['name']
        
    name = models.CharField(max_length=500)
    json = models.TextField()
        
    def __unicode__(self):
        return self.name