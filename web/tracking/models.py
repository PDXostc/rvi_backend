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
from django.db.models import signals
from django.core.exceptions import ValidationError
from django.utils.dateparse import parse_datetime

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
    
    @property
    def geom(self):
        geom = {'type': 'Point', 'coordinates': [self.loc_longitude,self.loc_latitude]}
        return (geom)

    
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
                
    def get_vehicle_name(self):
        """
        Returns the name of the vehicle associated with this Location
        """
        return self.loc_vehicle.get_name()
        

class Waypoints(models.Model):
    """
    Waypoints description
    This class dynamically creates a GEOJson field containing all the locations of the
    vehicle. This is then used to draw the waypoints line on the map.
    """
    
    wp_vehicle = models.OneToOneField(Vehicle, primary_key=True, verbose_name='Vehicle')
    from_time = datetime.datetime(1970,1,1,0,0,0,tzinfo=pytz.UTC)
    to_time = datetime.datetime(9999,12,31,23,59,59,tzinfo=pytz.UTC)
    locations = None
    

    @classmethod
    def set_time_utc(cls, from_time, to_time):        
        cls.from_time = pytz.utc.localize(parse_datetime(from_time))
        cls.to_time = pytz.utc.localize(parse_datetime(to_time))

    @property
    def geom(self):
        """
        Returns the waypoints as LineString object for direct use with GeoJSON.
        """
        geom = {'type': 'LineString', 'coordinates': [list(e) for e in self.select_locations().values_list('loc_longitude','loc_latitude','loc_altitude','loc_time','loc_speed','loc_climb','loc_odometer')]}
        return (geom)
        
    @property
    def start_location(self):
        """
        Returns the start location or first waypoint of the list.
        Note: We need to flip latitude and longitude as Leaflet expects latitude first.
        """
        locations = self.select_locations()
        if len(locations) > 0:
            return list(locations.values_list('loc_latitude','loc_longitude','loc_time','loc_speed'))[0]
            
    @property
    def end_location(self):
        """
        Returns end last location or last waypoint of the list.
        Note: We need to flip latitude and longitude as Leaflet expects latitude first.
        """
        locations = self.select_locations()
        if len(locations) > 0:
            return list(locations.values_list('loc_latitude','loc_longitude','loc_time','loc_speed'))[-1]
            
    @property
    def location_info(self):
        """
        Returns additional information time, speed, odometer for each waypoint
        """
        return list(self.select_locations().values_list('loc_time', 'loc_speed', 'loc_odometer'))
            
    @property
    def vehicle_info(self):
        return [self.wp_vehicle.veh_name, self.wp_vehicle.get_picture()]
        
    def select_locations(self):
        """
        Returns a list with all waypoints as [[long1, lat1], [long2, lat2], ...]
        Note: GeoJSON expects [long, lat] while Leaflet uses [lat, long]
        """
        if not self.locations:
            self.locations = Location.objects.filter(loc_vehicle=self.wp_vehicle, loc_time__range=(Waypoints.from_time, Waypoints.to_time)).order_by('loc_time')
        return self.locations
        

class Position(models.Model):
    """
    Position description
    This class dynamically creates a GEOJson field containing the position of a vehicle
    according to at_time. The date/time of the actual position may be earlier than at_time
    but never later.
    """
    
    wp_vehicle = models.OneToOneField(Vehicle, primary_key=True, verbose_name='Vehicle')
    at_time = datetime.datetime(9999,12,31,23,59,59,tzinfo=pytz.UTC)
    location = None
    

    @classmethod
    def set_time_utc(cls, at_time):        
        cls.at_time = pytz.utc.localize(parse_datetime(at_time))

    @property
    def geom(self):
        """
        Returns the position as a Point object for direct use with GeoJSON.
        """
        position = self.select_location()
        if position:
            geom = {'type': 'Point', 'coordinates': [position[0].loc_longitude,position[0].loc_latitude]}
        else:
            geom = {'type': 'Point', 'coordinates': [0,51.48]}
        return (geom)
        
    @property
    def vehicle_info(self):
        position = self.select_location()
        if position:
            return [self.wp_vehicle.veh_name, self.wp_vehicle.get_picture(), position[0].loc_time, position[0].loc_speed]
        else:
            return [self.wp_vehicle.veh_name, self.wp_vehicle.get_picture()]
                
    def select_location(self):
        """
        Returns a list with all waypoints as [[long1, lat1], [long2, lat2], ...]
        Note: GeoJSON expects [long, lat] while Leaflet uses [lat, long]
        """
        if not self.location:
            self.location = Location.objects.filter(loc_vehicle=self.wp_vehicle, loc_time__lt=(Position.at_time)).order_by('-loc_time')
        return self.location


def createVehicleDependentRecords(sender, instance, created, **kwargs):
    """
    Automatically create a record in the database for all dependent one-to-one tables
    when a Vehicle record is created.
    """
    if created:
        Waypoints.objects.create(wp_vehicle=instance)
        Position.objects.create(wp_vehicle=instance)
        
signals.post_save.connect(createVehicleDependentRecords, sender=Vehicle, weak=False, dispatch_uid='models.createVehicleDependentRecords')
