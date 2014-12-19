from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, loader

from vehicles.models import Vehicle
from sota.models import Update


def dashboard(request):
    template = loader.get_template('rvi/home.html')

    vehicles = Vehicle.objects.all()
    updates = Update.objects.all()
    
    context = RequestContext(request, {
        'title' : 'Dashboard',
        'vehicles' : vehicles,
        'updates' : updates,
    })
    
    return HttpResponse(template.render(context))
