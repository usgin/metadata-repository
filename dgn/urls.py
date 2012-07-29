from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^metadata/', include('metadatadb.urls')),
    url(r'^registry/', include('registry.urls')),
    url(r'^accounts/login', 'django.contrib.auth.views.login', {'template_name': 'accounts/login.jade'}),
    url(r'^accounts/logout', 'django.contrib.auth.views.logout_then_login'),
    url(r'^accounts/profile', 'ui.accounts.profile'),
    url(r'^accounts/register', 'ui.accounts.register'),
    url(r'^repository/', include('ui.repository_urls'))
)
