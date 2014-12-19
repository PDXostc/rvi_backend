from django.conf.urls import patterns, url

from tracking import views

urlpatterns = patterns('',
    url(r'^tracking/$', views.tracking, name='tracking'),


    url(r'^tracking/(?P<from_date>[0-9]{4}-[0-9]{2}-[0-9]{2})\+(?P<from_time>[0-9]{2}:[0-9]{2}:[0-9]{2})/$', views.tracking, name='tracking'),

    url(r'^tracking/(?P<from_date>[0-9]{4}-[0-9]{2}-[0-9]{2})\+(?P<from_time>[0-9]{2}:[0-9]{2}:[0-9]{2})_(?P<to_date>[0-9]{4}-[0-9]{2}-[0-9]{2})\+(?P<to_time>[0-9]{2}:[0-9]{2}:[0-9]{2})/$', views.tracking, name='tracking'),

    url(r'^tracking/(?P<from_date>[0-9]{4}-[0-9]{2}-[0-9]{2})_(?P<to_date>[0-9]{4}-[0-9]{2}-[0-9]{2})/$', views.tracking, name='tracking'),

    url(r'^tracking/(?P<from_date>[0-9]{4}-[0-9]{2}-[0-9]{2})/$', views.tracking, name='tracking'),

    url(r'^tracking/_(?P<to_date>[0-9]{4}-[0-9]{2}-[0-9]{2})/$', views.tracking, name='tracking'),


    url(r'^tracking/(?P<vehicle_id>\d+)/(?P<from_date>[0-9]{4}-[0-9]{2}-[0-9]{2})\+(?P<from_time>[0-9]{2}:[0-9]{2}:[0-9]{2})_(?P<to_date>[0-9]{4}-[0-9]{2}-[0-9]{2})\+(?P<to_time>[0-9]{2}:[0-9]{2}:[0-9]{2})/$', views.tracking, name='tracking'),

    url(r'^tracking/(?P<vehicle_id>\d+)/(?P<from_date>[0-9]{4}-[0-9]{2}-[0-9]{2})_(?P<to_date>[0-9]{4}-[0-9]{2}-[0-9]{2})/$', views.tracking, name='tracking'),

    url(r'^tracking/(?P<vehicle_id>\d+)/(?P<from_date>[0-9]{4}-[0-9]{2}-[0-9]{2})/$', views.tracking, name='tracking'),

    url(r'^tracking/(?P<vehicle_id>\d+)/_(?P<to_date>[0-9]{4}-[0-9]{2}-[0-9]{2})/$', views.tracking, name='tracking'),

    url(r'^tracking/(?P<vehicle_id>\d+)/$', views.tracking, name='tracking'),

    url(r'^tracking/(?P<vehicle_id>\d+)/(?P<from_date>[0-9]{4}-[0-9]{2}-[0-9]{2})\+(?P<from_time>[0-9]{2}:[0-9]{2}:[0-9]{2})/$', views.tracking, name='tracking'),


    url(r'^replay/$', views.replay, name='replay'),


    url(r'^replay/(?P<from_date>[0-9]{4}-[0-9]{2}-[0-9]{2})\+(?P<from_time>[0-9]{2}:[0-9]{2}:[0-9]{2})/$', views.replay, name='replay'),

    url(r'^replay/(?P<from_date>[0-9]{4}-[0-9]{2}-[0-9]{2})\+(?P<from_time>[0-9]{2}:[0-9]{2}:[0-9]{2})_(?P<to_date>[0-9]{4}-[0-9]{2}-[0-9]{2})\+(?P<to_time>[0-9]{2}:[0-9]{2}:[0-9]{2})/$', views.replay, name='replay'),

    url(r'^replay/(?P<from_date>[0-9]{4}-[0-9]{2}-[0-9]{2})_(?P<to_date>[0-9]{4}-[0-9]{2}-[0-9]{2})/$', views.replay, name='replay'),

    url(r'^replay/(?P<from_date>[0-9]{4}-[0-9]{2}-[0-9]{2})/$', views.replay, name='replay'),

    url(r'^replay/_(?P<to_date>[0-9]{4}-[0-9]{2}-[0-9]{2})/$', views.replay, name='replay'),


    url(r'^replay/(?P<vehicle_id>\d+)/(?P<from_date>[0-9]{4}-[0-9]{2}-[0-9]{2})\+(?P<from_time>[0-9]{2}:[0-9]{2}:[0-9]{2})_(?P<to_date>[0-9]{4}-[0-9]{2}-[0-9]{2})\+(?P<to_time>[0-9]{2}:[0-9]{2}:[0-9]{2})/$', views.replay, name='replay'),

    url(r'^replay/(?P<vehicle_id>\d+)/(?P<from_date>[0-9]{4}-[0-9]{2}-[0-9]{2})_(?P<to_date>[0-9]{4}-[0-9]{2}-[0-9]{2})/$', views.replay, name='replay'),

    url(r'^replay/(?P<vehicle_id>\d+)/(?P<from_date>[0-9]{4}-[0-9]{2}-[0-9]{2})/$', views.replay, name='replay'),

    url(r'^replay/(?P<vehicle_id>\d+)/_(?P<to_date>[0-9]{4}-[0-9]{2}-[0-9]{2})/$', views.replay, name='replay'),

    url(r'^replay/(?P<vehicle_id>\d+)/$', views.replay, name='replay'),

    url(r'^replay/(?P<vehicle_id>\d+)/(?P<from_date>[0-9]{4}-[0-9]{2}-[0-9]{2})\+(?P<from_time>[0-9]{2}:[0-9]{2}:[0-9]{2})/$', views.replay, name='replay'),


    url(r'^location/$', views.location, name='location'),

    url(r'^location/(?P<at_date>[0-9]{4}-[0-9]{2}-[0-9]{2})/$', views.location, name='location'),

    url(r'^location/(?P<at_date>[0-9]{4}-[0-9]{2}-[0-9]{2})\+(?P<at_time>[0-9]{2}:[0-9]{2}:[0-9]{2})/$', views.location, name='location'),

    url(r'^location/(?P<vehicle_id>\d+)/(?P<at_date>[0-9]{4}-[0-9]{2}-[0-9]{2})/$', views.location, name='location'),

    url(r'^location/(?P<vehicle_id>\d+)/(?P<at_date>[0-9]{4}-[0-9]{2}-[0-9]{2})\+(?P<at_time>[0-9]{2}:[0-9]{2}:[0-9]{2})/$', views.location, name='location'),

    url(r'^location/(?P<vehicle_id>\d+)/$', views.location, name='location'),


    url(r'^realtime/$', views.realtime, name='realtime'),

    url(r'^realtime/(?P<vehicle_id>\d+)/$', views.realtime, name='realtime'),


    url(r'^test/$', views.test, name='test'),

    url(r'^$', views.index, name='tracking_index'),


)
