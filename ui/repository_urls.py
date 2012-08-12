from django.conf.urls import patterns, url

urlpatterns = patterns('ui.repository',
    url(r'^$', 'home'),
    url(r'^browse/', 'browse'),
    url(r'^search/(?P<term>.*)$', 'search'),
    url(r'^harvest/', 'harvest'),
    url(r'^contact/$', 'contact'),
    url(r'^about/$', 'about'),
    url(r'^terms/$', 'terms'),
    url(r'^on-metadata/$', 'rant'),
    url(r'^sitemap.xml$', 'sitemap'),
    url(r'^resource/new$', 'new'),
    url(r'^resource/(?P<resourceId>.*)/edit$', 'edit'),
    url(r'^resource/(?P<resourceId>.*)/$', 'resource'),  
    url(r'^collection/(?P<collectionId>.*)/$', 'collection'),
    url(r'^collection/(?P<collectionId>.*)\.json', 'populateCollection'),
    url(r'^collection/(?P<collectionId>.*)/resource/new', 'collection_resource'),                     
) 