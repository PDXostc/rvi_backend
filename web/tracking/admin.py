"""
Copyright (C) 2014, Jaguar Land Rover

This program is licensed under the terms and conditions of the
Mozilla Public License, version 2.0.  The full text of the 
Mozilla Public License is at https://www.mozilla.org/MPL/2.0/

Maintainer: Rudolf Streif (rstreif@jaguarlandrover.com) 
"""

from django.contrib import admin

from tracking.models import Location

class LocationAdmin(admin.ModelAdmin):
    """
    Administration view for Location
    """
    fieldsets = [
        (None,        {'fields': [('loc_vehicle', 'loc_time')]}),
        ('Location',  {'fields': [('loc_longitude', 'loc_latitude', 'loc_altitude')]}),
        ('Motion',    {'fields': [('loc_speed', 'loc_climb', 'loc_track')]}),
        ('Vehcile',   {'fields': [('loc_odometer')]}),
    ]
    
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['loc_vehicle', 'loc_time', 'loc_latitude', 'loc_longitude',
                    'loc_altitude', 'loc_speed', 'loc_climb', 'loc_track', 'loc_odometer']
        else:
            return ['loc_vehicle']



admin.site.register(Location, LocationAdmin)
