"""
Copyright (C) 2014, Jaguar Land Rover

This program is licensed under the terms and conditions of the
Mozilla Public License, version 2.0.  The full text of the 
Mozilla Public License is at https://www.mozilla.org/MPL/2.0/

Rudolf Streif (rstreif@jaguarlandrover.com) 

Anson Fan (afan1@jaguarlandrover.com)
"""

from __future__ import absolute_import

from dateutil.parser import parse
import sys, os, logging, time, jsonrpclib, base64, calendar
import Queue

from urlparse import urlparse

from django.conf import settings

import dynamicagents.models
import time


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
    retry.ret_update_da.set_status(status)

    
def get_destination(retry):
    """
    Return vehicles.Vehicle and vehicle URL from a Retry object
    :param retry: sota.models.Retry object
    """
    vehicle = retry.ret_update_da.upd_vehicle
    dst_url = vehicle.veh_rvibasename + '/vin/' + vehicle.veh_vin
    return [vehicle, dst_url]

def terminate_agent(retry):
    logger.info("Terminating an agent")

    global transaction_id

    # get settings
    # service edge url
    try:
        rvi_service_url = settings.RVI_SERVICE_EDGE_URL
    except NameError:
        logger.error('%s: RVI_SERVICE_EDGE_URL not defined. Check settings!', retry)
        set_status(retry, dynamicagents.models.Status.FAILED)
        return False
    # SOTA service id
    try:
        rvi_service_id = settings.RVI_DA_SERVICE_ID
    except NameError:
        rvi_service_id = '/dynamicagents'

    rvi_server = None
    logger.info('%s: Establishing RVI service edge connection: %s', retry, rvi_service_url)
    try:
        rvi_server = jsonrpclib.Server(rvi_service_url)
    except Exception as e:
        logger.error('%s: Cannot connect to RVI service edge: %s', retry, e)
        set_status(retry, dynamicagents.models.Status.FAILED)
        return False
    logger.info('%s: Established connection to RVI Service Edge: %s', retry, rvi_server)

    # get package to update and open file
    agent = retry.ret_update_da.upd_package_da
    agent_name = agent.pac_name_da

    vehicle = retry.ret_update_da.upd_vehicle_da
    dst_url = vehicle.veh_rvibasename + '/vin/' + vehicle.veh_vin
 
    # notify remote of pending file transfer
    transaction_id += 1
    
    try:

        rvi_server.message(calling_service = rvi_service_id,
                           service_name = dst_url + rvi_service_id + '/terminate_agent',
                           transaction_id = str(transaction_id),
                           timeout = int(time.time()+60),
                           parameters = {u'agent':agent_name}
                           )

    except Exception as e:
        logger.error('%s: Cannot send request: %s', retry, e)
        set_status(retry, dynamicagents.models.Status.FAILED)
        return False
    
    logger.info('%s: Notified remote of pending file transfer.', retry)
    
    # done
    set_status(retry, dynamicagents.models.Status.TERMINATED)
    logger.info('%s: Completed Update.', retry)
    return True    

def notify_update(retry):
    """
    Notify destination, typically a vehicle, of a pending software
    update.
    :param retry: sota.models.Retry object
    """
    
    logger.info('%s: Running Update.', retry)
    set_status(retry, dynamicagents.models.Status.STARTED)
    
    global transaction_id
    
    # get settings
    # service edge url
    try:
        rvi_service_url = settings.RVI_SERVICE_EDGE_URL
    except NameError:
        logger.error('%s: RVI_SERVICE_EDGE_URL not defined. Check settings!', retry)
        set_status(retry, dynamicagents.models.Status.FAILED)
        return False
    # SOTA service id
    try:
        rvi_service_id = settings.RVI_DA_SERVICE_ID
    except NameError:
        rvi_service_id = '/dynamicagents'

    # establish outgoing RVI service edge connection
    rvi_server = None
    logger.info('%s: Establishing RVI service edge connection: %s', retry, rvi_service_url)
    try:
        rvi_server = jsonrpclib.Server(rvi_service_url)
    except Exception as e:
        logger.error('%s: Cannot connect to RVI service edge: %s', retry, e)
        set_status(retry, dynamicagents.models.Status.FAILED)
        return False
    logger.info('%s: Established connection to RVI Service Edge: %s', retry, rvi_server)
    
    # get package to update and open file
    agent = retry.ret_update_da.upd_package_da
    agent_name = agent.pac_name_da
    agent_launch_cmd = str(agent.pac_start_cmd)
    agent_expiration = calendar.timegm(parse(str(retry.ret_update_da.upd_expiration)).timetuple())
    agent_file_dst = agent.pac_file_da
    
    agent_file_dst.open(mode='r')
    agentcode = agent_file_dst.read()
    agent_file_dst.close()

    vehicle = retry.ret_update_da.upd_vehicle_da
    dst_url = vehicle.veh_rvibasename + '/vin/' + vehicle.veh_vin
 
    # notify remote of pending file transfer
    transaction_id += 1
    try:
        # rvi_server.message(calling_service = rvi_service_id,
        #                    service_name = dst_url + rvi_service_id + '/notify',
        #                    transaction_id = str(transaction_id),
        #                    timeout = int(retry.get_timeout_epoch()),
        #                    parameters = [{ u'agent': agent_name },
        #                                  { u'retry': retry.pk },
        #                                 ])

        rvi_server.message(calling_service = rvi_service_id,
                           service_name = dst_url + rvi_service_id + '/agent',
                           transaction_id = str(transaction_id),
                           timeout = int(retry.get_timeout_epoch()),
                           parameters = {u'agent':agent_name, u'launch':agent_launch_cmd,u'expires':str(agent_expiration),
                                            u'agent_code':(base64.b64encode(agentcode.encode('UTF-8')))}
                           )

    except Exception as e:
        logger.error('%s: Cannot send request: %s', retry, e)
        set_status(retry, dynamicagents.models.Status.FAILED)
        return False
    
    logger.info('%s: Notified remote of pending file transfer.', retry)
    
    # done
    set_status(retry, dynamicagents.models.Status.SUCCESS)
    logger.info('%s: Completed Update.', retry)
    return True



