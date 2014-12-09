import json

from django.shortcuts import render

from django.http import HttpResponse
from django.template import RequestContext, loader
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.dateparse import parse_datetime
import pytz

from django.db.models import Avg, Min, Max, Count

from tracking.models import Location
from tracking.models import Waypoints
from tracking.models import Position
from vehicles.models import Vehicle


def get_waypoints(vehicle_id=-1, from_date='1970-01-01', to_date='9999-12-31', from_time='00:00:00', to_time='23:59:59'):
    range_start = from_date + ' ' + from_time
    range_end   = to_date + ' ' + to_time
    print(range_start, range_end)
    Waypoints.set_time_utc(range_start, range_end)
    if vehicle_id == -1:
        return Waypoints.objects.all()
    else:
        return Waypoints.objects.filter(wp_vehicle_id=vehicle_id)
    

def get_position(vehicle_id=-1, at_date='9999-12-31', at_time='23:59:59'):
    Position.set_time_utc(at_date + ' ' + at_time)
    if vehicle_id == -1:
        return Position.objects.all()
    else:
        return Position.objects.filter(wp_vehicle_id=vehicle_id)

        


def tracking(request, vehicle_id=-1, from_date='1970-01-01', to_date='9999-12-31', from_time='00:00:00', to_time='23:59:59'):
    template = loader.get_template('tracking/tracking.html')
    
    waypoints = get_waypoints(vehicle_id, from_date, to_date, from_time, to_time)

    context = RequestContext(request, {
        'waypoints': waypoints,
    })

    return HttpResponse(template.render(context))



def replay(request, vehicle_id=-1, from_date='1970-01-01', to_date='9999-12-31', from_time='00:00:00', to_time='23:59:59'):
    template = loader.get_template('tracking/replay.html')
    
    waypoints = get_waypoints(vehicle_id, from_date, to_date, from_time, to_time)
    
    context = RequestContext(request, {
        'waypoints': waypoints,
    })

    return HttpResponse(template.render(context))



def location(request, vehicle_id=-1, at_date='9999-12-31', at_time='23:59:59'):
    template = loader.get_template('tracking/location.html')
    
    position = get_position(vehicle_id, at_date, at_time)

    context = RequestContext(request, {
        'position': position,
    })
    
    return HttpResponse(template.render(context))


def index(request):
    template = loader.get_template('tracking/index.html')
    
    maps = [{'id':'location','name':'Location'},{'id':'tracking','name':'Tracking'},{'id':'replay','name':'Replay'}]
    vehicles = Vehicle.objects.all()
    
    print vehicles

    context = RequestContext(request, {
        'maps': maps,
        'vehicles': vehicles,
    })
    
    return HttpResponse(template.render(context))
