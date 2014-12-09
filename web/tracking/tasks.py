"""
Copyright (C) 2014, Jaguar Land Rover

This program is licensed under the terms and conditions of the
Mozilla Public License, version 2.0.  The full text of the 
Mozilla Public License is at https://www.mozilla.org/MPL/2.0/

Rudolf Streif (rstreif@jaguarlandrover.com) 
"""

from __future__ import absolute_import

import sys, os, logging, time, jsonrpclib, base64
import Queue

from urlparse import urlparse

from django.conf import settings

import sota.models


# Logging setup
logger = logging.getLogger('rvi')

# Globals
transaction_id = 0


def subscribe(vehicle, channels, interval=5):
    """
    Subscribe to reporting channels on a vehicle
    :param vehicle:  Vehicle object
    :param channels: List with channels
    :param interval: Reporting interval in [ms]
                     > 0: report every interval [ms]
                     = 0: unsubscribe
                     < 0: report at the absolute time
    """
    
    logger.info('Subscribing to %s on %s.', channels, vehicle)
    
    global transaction_id
    
    # get settings
    # service edge url
    try:
        rvi_service_url = settings.RVI_SERVICE_EDGE_URL
    except NameError:
        logger.error('RVI_SERVICE_EDGE_URL not defined. Check settings!')
        return False

    # Tracking service id
    try:
        rvi_service_id = settings.RVI_TRACKING_SERVICE_ID
    except NameError:
        rvi_service_id = '/logging'

    # get destination info
    dst_url = vehicle.veh_rvibasename + '/vin/' + vehicle.veh_vin
 
    # establish outgoing RVI service edge connection
    rvi_server = None
    logger.info('Establishing RVI service edge connection: %s', rvi_service_url)
    try:
        rvi_server = jsonrpclib.Server(rvi_service_url)
    except Exception as e:
        logger.error('Cannot connect to RVI service edge: %s', e)
        return False
    logger.info('Established connection to RVI Service Edge: %s', rvi_server)
    
    # notify remote of subscription
    transaction_id += 1
    if interval == 0:
        # unsubscribe
        rvi_server.message(calling_service = rvi_service_id,
                           service_name = dst_url + rvi_service_id + '/unsubscribe',
                           transaction_id = str(transaction_id),
                           timeout = int(time.time()) + 60,
                           parameters = [{ u'channels': channels },
                                        ])
    else:
        # subscribe
        rvi_server.message(calling_service = rvi_service_id,
                           service_name = dst_url + rvi_service_id + '/subscribe',
                           transaction_id = str(transaction_id),
                           timeout = int(time.time()) + 60,
                           parameters = [{ u'channels': channels },
                                         { u'reporting_interval': interval },
                                        ])
        
    logger.info('Notified remote of subscription.')
    
    # done
    return True


def unsubscribe(vehicle, channels):
    """
    Unsubscribe from reporting channels on a vehicle
    :param vehicle:  Vehicle object
    :param channels: List with channels
    """
    return subscribe(vehicle, channels, 0)


