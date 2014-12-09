"""
Copyright (C) 2014, Jaguar Land Rover

This program is licensed under the terms and conditions of the
Mozilla Public License, version 2.0.  The full text of the 
Mozilla Public License is at https://www.mozilla.org/MPL/2.0/

Maintainer: Rudolf Streif (rstreif@jaguarlandrover.com) 
"""

"""
Software Over The Air (SOTA) services.
"""

import os, threading, base64
import time
from urlparse import urlparse
import Queue
from rvijsonrpc import RVIJSONRPCServer

import __init__
from __init__ import __RVI_LOGGER__ as logger

from vehicles.models import Vehicle
from tracking.models import Location


# Tracking Callback Server
class TrackingCallbackServer(threading.Thread):
    """
    RPC server thread responding to Tracking callbacks from the RVI framework
    """
    
    def __init__(self, service_edge, callback_url, service_id):
        self.service_edge = service_edge
        self.service_id = service_id
        self.callback_url = callback_url
        threading.Thread.__init__(self)
        url = urlparse(self.callback_url)
        self.localServer =  RVIJSONRPCServer(addr=((url.hostname, url.port)), logRequests=False)
        self.register_services()
        
    def register_services(self):
        # register callback functions with RPC server
        self.localServer.register_function(report, self.service_id + "/report")
        
        # register services with RVI framework
        result = self.service_edge.register_service(service = self.service_id+'/report',
                                               network_address = self.callback_url)
        logger.info('Tracking Service Registration: Report service name: %s', result['service'])

    def run(self):
        self.localServer.serve_forever()
        
    def shutdown(self):
        self.localServer.shutdown()
 
        
# Callback functions
def report(timestamp, vin, data):
    logger.info('Tracking Callback Server: Report request: Time: %s, VIN: %s, Data: %s.', timestamp, vin, data)

    # get the vehicle record from the database
    try:
        vehicle = Vehicle.objects.get(veh_vin = vin)
    except Exception as e:
        logger.error("Tracking Callback Server: Cannot retrieve vehicle '%s' from database. Error: %s", vin, e)
        return {u'status': 0}

    location = Location()
    location.loc_vehicle = vehicle
    location.loc_time = timestamp

    for channel in data:
        key = channel['channel']
        value = channel['value']
        if key == 'location':
            location.loc_latitude = value['lat']
            location.loc_longitude = value['lon']
            location.loc_altitude = value['alt']
        elif key == 'speed':
            location.loc_speed = float(value)
        elif key == 'odometer':
            location.loc_odometer = float(value)

    location.save()

    return {u'status': 0}


"""
    


    # create and save the location record
    location = Location()
    location.loc_vehicle = vehicle
    location.loc_timestamp = timestamp
    location.loc_latitude = waypoint['lat']
    location.loc_longitude = waypoint['long']
    location.loc_altitude = waypoint['alt']
    location.loc_speed = channeldata['speed']
    location.loc_odometer = channeldata['odo']
    location.save()
"""

