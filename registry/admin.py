from models import Resource, ResourceCollection, Contact
from django.contrib import admin

class ResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'metadata_id', 'edit_metadata_link', 'published')
    filter_horizontal = ['editors', 'collections']
    list_filter = ('published', 'collections')
    search_fields = ['title', 'metadata_id']
    
class ResourceCollectionAdmin(admin.ModelAdmin):
    filter_horizontal = [ 'editors', 'parents' ]
    list_display = ('title', 'collection_id')
    search_fields = ['title', 'collection_id']
    
admin.site.register(Resource, ResourceAdmin)
admin.site.register(ResourceCollection, ResourceCollectionAdmin)
admin.site.register(Contact)
