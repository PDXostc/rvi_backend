"""
Copyright (C) 2014, Jaguar Land Rover

This program is licensed under the terms and conditions of the
Mozilla Public License, version 2.0.  The full text of the 
Mozilla Public License is at https://www.mozilla.org/MPL/2.0/

Rudolf Streif (rstreif@jaguarlandrover.com) 
"""

import datetime, pytz, uuid, jwt
from django.db import models
from django.utils.safestring import mark_safe
from common.models import Account
from vehicles.models import Vehicle
from security.models import JSONWebKey


class Device(Account):
    """
    Data model for a mobile device which can be a smartphone,
    tablet, wearable, etc.
    """
    dev_name    = models.CharField('Device Name', max_length=256)
    dev_owner   = models.CharField('Owner', max_length=256)
    dev_mdn     = models.CharField('Phone Number', max_length=256)
    dev_min     = models.CharField('Mobile Identification Number', max_length=256, null=True, blank=True)
    dev_imei    = models.CharField('Mobile Equipment Identifier', max_length=256, null=True, blank=True)
    dev_wifimac = models.CharField('WiFi MAC', max_length=256, null=True, blank=True)
    dev_btmac   = models.CharField('Bluetooth MAC', max_length=256, null=True, blank=True)
    dev_uuid    = models.CharField('UUID', max_length=256)
    dev_key     = models.OneToOneField(JSONWebKey, verbose_name = 'Key', null=True)
    dev_rvibasename = models.CharField('RVI Domain', max_length=256)

    class Meta:
        verbose_name_plural = "Devices"

    def get_name(self):
        return self.dev_name
		
    def __unicode__(self):
		return 	self.dev_name

    def get_rvi_id(self):
        return self.dev_rvibasename + '/mobile/' + self.dev_uuid
		


class Remote(models.Model):
    """
    Data model for remote controls that enable a Device to carry out
    certain actions on a Vehicle.
    """
    rem_name      = models.CharField('Remote Name', max_length=256)
    rem_uuid      = models.CharField('Remote UUID', max_length=60, editable=False, unique=True)
    rem_device    = models.ForeignKey(Device, verbose_name='Device')
    rem_vehicle   = models.ForeignKey(Vehicle, verbose_name='Vehicle')
    rem_created   = models.DateTimeField(auto_now_add=True, editable=False)
    rem_updated   = models.DateTimeField(auto_now=True, editable=False)
    rem_validfrom = models.DateTimeField('Valid From', max_length=100)
    rem_validto   = models.DateTimeField('Valid To', max_length=100)
    rem_lock      = models.BooleanField('Lock/Unlock', default=False)
    rem_engine    = models.BooleanField('Start/Stop Engine', default=False)
    rem_trunk     = models.BooleanField('Open/Close Trunk', default=False)
    rem_horn      = models.BooleanField('Honk Horn', default=False)
    rem_lights    = models.BooleanField('Turn On/Off Lights', default=False)
    rem_windows   = models.BooleanField('Open/Close Windows', default=False)
    rem_hazard    = models.BooleanField('Flash Hazard Lights', default=False)
    _controls = [
        ('lock',    rem_lock),
        ('engine',  rem_engine),
        ('trunk',   rem_trunk),
        ('horn',    rem_horn),
        ('lights',  rem_lights),
        ('windows', rem_windows),
        ('hazard',  rem_hazard),
    ]

    class Meta:
        verbose_name_plural = "Remotes"

    def get_name(self):
        return self.rem_name
		
    def __unicode__(self):
		return 	self.rem_name
        
    def format_json(self):
        jr = {}
        jr[u'sources'] = [self.rem_device.get_rvi_id(),]
        jr[u'destinations'] = []
        for control in self._controls:
            if control[1]:
                jr[u'destinations'].append(self.rem_vehicle.get_rvi_id() + '/control/' + control[0])
        jr[u'keys'] = []
        jr[u'keys'].append(self.rem_device.dev_key.format_json_public_key(use = JSONWebKey.USE_TYPE_SIG))
        jr[u'validity'] = {
            u'start' : self._get_time_epoch(self.rem_validfrom),
            u'stop'  : self._get_time_epoch(self.rem_validto)
        }
        jr[u'create_timestamp'] = self._get_time_epoch(self.rem_created)
        jr[u'id'] = self.rem_uuid
        return jr
        
    def encode_jwt(self, key, algorithm='RS256'):
        jr = self.format_json()
        return jwt.encode(jr, key, algorithm)
        
    def _get_time_epoch(self, dt):
        return int((dt.astimezone(pytz.UTC) - datetime.datetime(1970,1,1,tzinfo=pytz.UTC)).total_seconds())

    def save(self, *args, **kwargs):
        self.rem_uuid = str(uuid.uuid4())
        super(Remote, self).save(*args, **kwargs)
