"""
Copyright (C) 2014, Jaguar Land Rover

This program is licensed under the terms and conditions of the
Mozilla Public License, version 2.0.  The full text of the 
Mozilla Public License is at https://www.mozilla.org/MPL/2.0/

Rudolf Streif (rstreif@jaguarlandrover.com) 
"""

from django.contrib import admin
from vehicles.models import Vehicle

# Register your models here.

class VehicleAdmin(admin.ModelAdmin):
    """
    Administration view for Vehicles.
    """
    fieldsets = [
        (None,                  {'fields': ['veh_name']}),
        ('Vehicle Information', {'fields': ['veh_make', 'veh_model', 'veh_vin', 'veh_year']}),
        ('RVI Information',     {'fields': ['veh_rvibasename']}),
    ]

admin.site.register(Vehicle, VehicleAdmin)

