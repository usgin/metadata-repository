from models import Resource, ResourceCollection, Contact
from django.contrib import admin

class ResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'metadata_link', 'published')
    filter_horizontal = ['editors', 'collections']
    list_filter = ('published', 'collections')

class ResourceCollectionAdmin(admin.ModelAdmin):
    filter_horizontal = [ 'editors', 'parents' ]
    
admin.site.register(Resource, ResourceAdmin)
admin.site.register(ResourceCollection, ResourceCollectionAdmin)
admin.site.register(Contact)
