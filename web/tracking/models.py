"""
Copyright (C) 2014, Jaguar Land Rover

This program is licensed under the terms and conditions of the
Mozilla Public License, version 2.0.  The full text of the 
Mozilla Public License is at https://www.mozilla.org/MPL/2.0/

Maintainer: Rudolf Streif (rstreif@jaguarlandrover.com) 
"""

import datetime, pytz

from django.utils import timezone
from django.db import models
from django.core.exceptions import ValidationError

from vehicles.models import Vehicle


class Location(models.Model):
    """
    Location description
    Tracks Vehicle locations
    """
    
    loc_vehicle = models.ForeignKey(Vehicle, verbose_name='Vehicle')
    loc_time = models.DateTimeField('Time')
    loc_latitude = models.FloatField('Latitude [deg]')
    loc_longitude = models.FloatField('Longitude [deg]')
    loc_altitude = models.FloatField('Altitude [m]', default=0)
    loc_speed = models.FloatField('Speed [m/s]', default=0)
    loc_climb = models.FloatField('Climb [m/s]', default=0)
    loc_track = models.FloatField('Track [deg]', default=0)
    loc_odometer = models.FloatField('Odometer [km]', default=0)
    
    def __unicode__(self):
        """
        Returns the Location string.
        """
        return self.to_string()

    def to_string(self):
        """
        Returns the Location string composed of
        <vehicle> on <time> at <longitude, latitude>.
        """
        return (self.loc_vehicle.get_name() +
                 " on " +
                 unicode(self.loc_time) +
                 " at (" +
                 str(self.loc_longitude) + ", " + str(self.loc_latitude) +
                 ")"
                 " going " +
                 str(self.loc_speed * 3.6) + " km/h"
                )

