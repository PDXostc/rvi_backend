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
from common.user import Account
from security.models import JSONWebKey
from security.models import CANFWKey

class RVIStatus:
    """
    Status values for RVI
    """
    OFFLINE  = "OF"
    ONLINE   = "ON"

def validate_veh_year(year):
    """
    Validation function for vehicle model year.
    :param year Year to validate
    """
    if not year.isdigit():
        raise ValidationError("Model year must be a number.")

class Vehicle(Account):
    """
    Data model for Vehicle
    """
    RVI_STATUS = (
        (RVIStatus.OFFLINE,  "Offline"),
        (RVIStatus.ONLINE,   "Online"),
    )
    veh_name = models.CharField('Vehicle Name', max_length=256)
    veh_make = models.CharField('Vehicle Make', max_length=256)
    veh_model = models.CharField('Vehicle Model', max_length=256)
    veh_picture = models.ImageField('Vehicle Picture', null=True, blank=True)
    veh_vin = models.CharField('Vehicle VIN', max_length=256)
    veh_year = models.CharField('Vehicle Model Year', max_length=4,null=True,blank=True, validators=[validate_veh_year])
    veh_rvibasename = models.CharField('RVI Domain', max_length=256)
    veh_rvistatus = models.CharField('RVI Status',
                                  max_length=2,
                                  choices=RVI_STATUS,
                                  default=RVIStatus.OFFLINE)
    veh_key = models.OneToOneField(JSONWebKey, verbose_name = 'Key', null=True)
    canfw_key = models.OneToOneField(CANFWKey, verbose_name = 'FW_Key', null=True)


    @property
    def veh_rvistatus_text(self):
        return dict(self.RVI_STATUS)[self.veh_rvistatus]
    
    def get_picture(self):
        if self.veh_picture:
            return self.veh_picture.url
        else:
            return settings.MEDIA_URL + settings.DEFAULT_VEHICLE_IMAGE
            
    def list_picture(self):
        return u'<img src="%s" width="50" />' % self.get_picture()
    list_picture.short_description = "Vehicle Image"
    list_picture.allow_tags = True
    
    def detail_picture(self):
        return u'<img src="%s" width="75" />' % self.get_picture()
    detail_picture.short_description = ""
    detail_picture.allow_tags = True
    
    def list_account(self):
        return self.account.username
    list_account.short_description = "Account"
    list_account.allow_tags = True
    
    def get_name(self):
        return self.veh_name
        
    def get_rvi_id(self):
        return self.veh_rvibasename + '/vin/' + self.veh_vin
		
    def __unicode__(self):
		return 	self.veh_name
		
