"""
Copyright (C) 2014, Jaguar Land Rover

This program is licensed under the terms and conditions of the
Mozilla Public License, version 2.0.  The full text of the 
Mozilla Public License is at https://www.mozilla.org/MPL/2.0/

Rudolf Streif (rstreif@jaguarlandrover.com) 
"""

from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'rvi.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    # for now redirect root to admin
    url(r'^', include(admin.site.urls)),
    url(r'^admin/', include(admin.site.urls)),
)

# uploaded files
urlpatterns += patterns('',
    (r'^files/(?P<path>.*)$', 'django.views.static.serve', {
    'document_root': settings.MEDIA_ROOT}))
