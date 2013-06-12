from models import Resource, ResourceCollection, Contact
from django.contrib import admin
from metadatadb.proxy import oneResource, proxyRequest
import json

def make_published(modeladmin, request, queryset):
    # Have to update CouchDB too...
    class DummyRequest():
        def __init__(self, method, user, body="{}"):
            self.method = method
            self.user = user
            self.body = body

    for record in queryset:
        # Get the full Record
        kwargs = {
            'path': '/metadata/record/' + record.metadata_id + '/',
            'method': 'GET'
        }
        original = proxyRequest(**kwargs)

        # Update it
        final = json.loads(original.content)
        final["Published"] = True

        # Send the update
        update = DummyRequest("PUT", request.user, json.dumps(final))
        result = oneResource(update, "record", record.metadata_id)
        print result

make_published.short_description = "Mark selected resources as published"

class ResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'couchDB_link', 'edit_metadata_link', 'published')
    filter_horizontal = ['editors', 'collections']
    list_filter = ('published', 'collections')
    search_fields = ['title', 'metadata_id']
    actions = [make_published]
    
class ResourceCollectionAdmin(admin.ModelAdmin):
    filter_horizontal = [ 'editors', 'parents' ]
    list_display = ('title', 'collection_id', 'couchDB_link')
    search_fields = ['title', 'collection_id']
    
admin.site.register(Resource, ResourceAdmin)
admin.site.register(ResourceCollection, ResourceCollectionAdmin)
admin.site.register(Contact)
