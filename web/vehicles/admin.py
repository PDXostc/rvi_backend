"""
Copyright (C) 2014, Jaguar Land Rover

This program is licensed under the terms and conditions of the
Mozilla Public License, version 2.0.  The full text of the 
Mozilla Public License is at https://www.mozilla.org/MPL/2.0/

Rudolf Streif (rstreif@jaguarlandrover.com) 
"""

from django.contrib import admin
from vehicles.models import Vehicle
import tracking.tasks


location_channels = ['location', 'speed', 'odometer']

class VehicleAdmin(admin.ModelAdmin):
    """
    Administration view for Vehicles.
    """
    fieldsets = [
        (None,                  {'fields': ['veh_name']}),
        ('Vehicle Information', {'fields': ['veh_make', 'veh_model', 'veh_vin', 'veh_year', 'veh_picture']}),
        ('RVI Information',     {'fields': ['veh_rvibasename']}),
    ]

    def subscribe_location(self, request, vehicles):
        for vehicle in vehicles:
            tracking.tasks.subscribe(vehicle, location_channels)
        self.message_user(request, "Location subscriptions sent to selected vehicles.")
    subscribe_location.short_description = "Subscribe to Location"

    def unsubscribe_location(self, request, vehicles):
        for vehicle in vehicles:
            tracking.tasks.unsubscribe(vehicle, location_channels)
        self.message_user(request, "Location subscription cancellations sent to selected vehicles.")
    unsubscribe_location.short_description = "Unsubscribe from Location"

    actions = [subscribe_location, unsubscribe_location]


admin.site.register(Vehicle, VehicleAdmin)

