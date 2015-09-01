"""
Copyright (C) 2014, Jaguar Land Rover

This program is licensed under the terms and conditions of the
Mozilla Public License, version 2.0.  The full text of the 
Mozilla Public License is at https://www.mozilla.org/MPL/2.0/

Rudolf Streif (rstreif@jaguarlandrover.com) 
"""

from django.conf import settings
from django.conf.urls import patterns, include, url
from django.views.generic import RedirectView
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'rvi.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    (r'', include('tokenapi.urls')),

    url(r'^tracking/', include('tracking.urls')),
    url(r'^sota/', include('sota.urls')),
    url(r'^admin/', include(admin.site.urls)),

    url(r'^$', 'auth.views.login_user'),
    url(r'^login/$', 'auth.views.login_user'),
    url(r'^history/$', 'servicehistory.views.history', name='history'),
    url(r'^keys/$', 'ownerportal.views.keys', name='keys'),
    url(r'^logout/$', 'auth.views.logout_user', name='logout'),
    # url(r'^logout/$', admin.auth.logout),
    # for now redirect root to admin
    #url(r'^', include(admin.site.urls)),
                       )

# uploaded files
urlpatterns += patterns('',
    (r'^files/(?P<path>.*)$', 'django.views.static.serve', {
    'document_root': settings.MEDIA_ROOT}))
