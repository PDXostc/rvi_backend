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
logger = logging.getLogger('rvi.sota')

# Globals
transaction_id = 0


def set_status(retry, status):
    """
    Convenience function to set the status of a Retry object
    and its associated Update object at the same time.
    :param retry: sota.models.Retry opbject
    :param status: status value from sota.models.Status
    """
    retry.set_status(status)
    retry.ret_update.set_status(status)

    
def get_destination(retry):
    """
    Return vehicles.Vehicle and vehicle URL from a Retry object
    :param retry: sota.models.Retry object
    """
    vehicle = retry.ret_update.upd_vehicle
    dst_url = vehicle.veh_rvibasename + '/vin/' + vehicle.veh_vin
    return [vehicle, dst_url]


def notify_update(retry):
    """
    Notify destination, typically a vehicle, of a pending software
    update.
    :param retry: sota.models.Retry object
    """
    
    logger.info('%s: Running Update.', retry)
    set_status(retry, sota.models.Status.STARTED)
    
    global transaction_id
    
    # get settings
    # service edge url
    try:
        rvi_service_url = settings.RVI_SERVICE_EDGE_URL
    except NameError:
        logger.error('%s: RVI_SERVICE_EDGE_URL not defined. Check settings!', retry)
        set_status(retry, sota.models.Status.FAILED)
        return False
    # SOTA service id
    try:
        rvi_service_id = settings.RVI_SOTA_SERVICE_ID
    except NameError:
        rvi_service_id = '/sota'

    # establish outgoing RVI service edge connection
    rvi_server = None
    logger.info('%s: Establishing RVI service edge connection: %s', retry, rvi_service_url)
    try:
        rvi_server = jsonrpclib.Server(rvi_service_url)
    except Exception as e:
        logger.error('%s: Cannot connect to RVI service edge: %s', retry, e)
        set_status(retry, sota.models.Status.FAILED)
        return False
    logger.info('%s: Established connection to RVI Service Edge: %s', retry, rvi_server)
    
    # get package to update and open file
    package = retry.ret_update.upd_package
    package_name = package.pac_name
    
    # get destination info
    vehicle = retry.ret_update.upd_vehicle
    dst_url = vehicle.veh_rvibasename + '/vin/' + vehicle.veh_vin
 
    # notify remote of pending file transfer
    transaction_id += 1
    rvi_server.message(calling_service = rvi_service_id,
                       service_name = dst_url + rvi_service_id + '/notify',
                       transaction_id = str(transaction_id),
                       timeout = int(retry.get_timeout_epoch()),
                       parameters = [{ u'package': package_name },
                                     { u'retry': retry.pk },
                                    ])
    logger.info('%s: Notified remote of pending file transfer.', retry)
    
    # done
    set_status(retry, sota.models.Status.WAITING)
    logger.info('%s: Completed Update.', retry)
    return True



