from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^contacts/$', 'registry.views.contacts'),
    url(r'^sync/', 'registry.utils.synch_to_couchdb'),                       
)                       