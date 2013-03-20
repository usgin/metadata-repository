from django.conf.urls import patterns, url

urlpatterns = patterns('metadatadb.proxy',
    url(r'^search/$', 'search'), # POST
    url(r'^(?P<resourceType>record|collection)/$', 'allResources'), # GET, POST
    url(r'^record\.(?P<viewFormat>iso.xml|atom.xml|geojson)$', 'viewRecords'), # GET
    url(r'^harvest/$', 'harvestRecord'), # POST
    url(r'^(?P<resourceType>record|collection)/(?P<resourceId>[^/]*)/$', 'oneResource'), # GET, PUT, DELETE
    url(r'^record/(?P<resourceId>[^/]*)\.(?P<viewFormat>iso.xml|atom.xml|geojson)$', 'viewRecord'), # GET
    url(r'^collection/(?P<resourceId>[^/]*)/records/$', 'getCollectionRecords'), # GET
    url(r'^collection/(?P<resourceId>[^/]*)/records\.(?P<viewFormat>iso.xml|atom.xml|geojson)$', 'viewCollectionRecords'), # GET
    url(r'^record/(?P<resourceId>[^/]*)/file/$', 'allFiles'), # GET, POST
    url(r'^record/(?P<resourceId>[^/]*)/file/(?P<fileName>.*)$', 'oneFile'), # GET, DELETE  
    url(r'^schema/$', 'allSchemas'), # GET
    url(r'^schema/(?P<schemaId>.*)/$', 'oneSchema'), # GET  
      
    url(r'^unauth/deleteUnpublishRecords/$', 'delUnpublish'), 
    url(r'^unauth/deleteCouchExtraRecords/$', 'delCouchExtraRec')             
)