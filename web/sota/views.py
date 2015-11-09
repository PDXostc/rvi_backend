"""
Copyright (C) 2014, Jaguar Land Rover

This program is licensed under the terms and conditions of the
Mozilla Public License, version 2.0.  The full text of the 
Mozilla Public License is at https://www.mozilla.org/MPL/2.0/

Barbara Harmon (bharmon@jaguarlandrover.com) 
"""
from django.shortcuts import render

from django.http import HttpResponse
from django.template import RequestContext, loader

def index(request):
	template = loader.get_template('sota/index.html')

	context = RequestContext(request, {
			'title' : 'SOTA (Software Updates Over the Air)',
		})

	return HttpResponse(template.render(context))

