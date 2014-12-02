"""
Copyright (C) 2014, Jaguar Land Rover

This program is licensed under the terms and conditions of the
Mozilla Public License, version 2.0.  The full text of the 
Mozilla Public License is at https://www.mozilla.org/MPL/2.0/

Rudolf Streif (rstreif@jaguarlandrover.com) 
"""

from django.db import models
from django.core.exceptions import ValidationError
from djgeojson.fields import PointField
from django.conf import settings


def validate_veh_year(year):
    """
    Validation function for vehicle model year.
    :param year Year to validate
    """
    if not year.isdigit():
        raise ValidationError("Model year must be a number.")

class Vehicle(models.Model):
    """
    Data model for Vehicle
    """
    veh_name = models.CharField('Vehicle Name', max_length=256)
    veh_make = models.CharField('Vehicle Make', max_length=256)
    veh_model = models.CharField('Vehicle Model', max_length=256)
    veh_picture = models.ImageField('Vehicle Picture', null=True, blank=True)
    veh_vin = models.CharField('Vehicle VIN', max_length=256)
    veh_year = models.CharField('Vehicle Model Year', max_length=4,null=True,blank=True, validators=[validate_veh_year])
    veh_rvibasename = models.CharField('RVI Basename', max_length=256)

    def get_picture(self):
        if self.veh_picture:
            return self.veh_picture.url
        else:
            return settings.MEDIA_URL + settings.DEFAULT_VEHICLE_IMAGE
        
    
    def get_name(self):
		return 	self.veh_name
    
    def __unicode__(self):
		return 	self.veh_name
		
