"""
Copyright (C) 2015, Jaguar Land Rover

This program is licensed under the terms and conditions of the
Mozilla Public License, version 2.0.  The full text of the 
Mozilla Public License is at https://www.mozilla.org/MPL/2.0/

Barbara Harmon (bharmon@jaguarlandrover.com) 
"""

from django.conf.urls import patterns, url

from sota import views

urlpatterns = patterns('',
	# The url() function is passed four arguments, 
	# two required: regex and view, and two optional: kwargs, and name. 

	# url(r'^sota/$', views.sota, name='sota'),
	
	url(r'^$', views.index, name='sota_index'),
)