"""
Copyright (C) 2015, Jaguar Land Rover

This program is licensed under the terms and conditions of the
Mozilla Public License, version 2.0.  The full text of the 
Mozilla Public License is at https://www.mozilla.org/MPL/2.0/

Rudolf Streif (rstreif@jaguarlandrover.com) 
"""

from __future__ import absolute_import
import hashlib
import hmac

import sys, os, logging, time, jsonrpclib, base64
import Queue

from urlparse import urlparse

from django.conf import settings

import can_fw.models


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
    retry.ret_udpate_fw.set_status(status)

    
def get_destination(retry):
    """
    Return vehicles.Vehicle and vehicle URL from a Retry object
    :param retry: sota.models.Retry object
    """
    vehicle = retry.ret_udpate_fw.upd_vehicle
    dst_url = vehicle.veh_rvibasename + '/vin/' + vehicle.veh_vin
    return [vehicle, dst_url]


def notify_update(retry):
    """
    Notify destination, typically a vehicle, of a pending software
    update.
    :param retry: sota.models.Retry object
    """
    
    logger.info('%s: Running Update.', retry)
    set_status(retry, can_fw.models.Status.STARTED)
    
    global transaction_id
    
    # get settings
    # service edge url
    try:
        rvi_service_url = settings.RVI_SERVICE_EDGE_URL
    except NameError:
        logger.error('%s: RVI_SERVICE_EDGE_URL not defined. Check settings!', retry)
        set_status(retry, can_fw.models.Status.FAILED)
        return False
    # SOTA service id
    try:
        rvi_service_id = settings.RVI_CANFW_SERVICE_ID
    except NameError:
        rvi_service_id = '/canfw'

    # establish outgoing RVI service edge connection
    rvi_server = None
    logger.info('%s: Establishing RVI service edge connection: %s', retry, rvi_service_url)
    try:
        rvi_server = jsonrpclib.Server(rvi_service_url)
    except Exception as e:
        logger.error('%s: Cannot connect to RVI service edge: %s', retry, e)
        set_status(retry, can_fw.models.Status.FAILED)
        return False
    logger.info('%s: Established connection to RVI Service Edge: %s', retry, rvi_server)
    
    # get package to update and open file
    package = retry.ret_udpate_fw.upd_package_fw
    package_name = package.pac_name
    
    # get destination info
    vehicle = retry.ret_udpate_fw.upd_vehicle_fw
    dst_url = vehicle.veh_rvibasename + '/vin/' + vehicle.veh_vin
    fw_key = vehicle.canfw_key.symm_key
    # hmac_obj = hmac.new(fw_key)
    # hmac_obj.update('Hello There')

    payload_array = []

    for prio_num in range(settings.RVI_CANFW_NUM_PRIO):
        try:
            rul_obj = getattr(package, 'prio_'+str(hex(prio_num)))
            rule_payload = {}
            send_payload = {}
            rule_payload['prio'] = "{0:0{1}x}".format(prio_num,2)
            rule_payload['mask'] = "{0:0{1}x}".format(int(rul_obj.mask, 16), 8)
            rule_payload['filt'] = "{0:0{1}x}".format(int(rul_obj.filt, 16), 8)
            rule_payload['id_xform'] = "{0:0{1}x}".format(int(rul_obj.id_xform, 16), 1)
            rule_payload['data_xform'] = "{0:0{1}x}".format(int(rul_obj.data_xform, 16), 1)
            rule_payload['id_operand'] = "{0:0{1}x}".format(int(rul_obj.id_operand,16), 8)
            rule_payload['data_operand'] = "{0:0{1}x}".format(int(rul_obj.data_operand, 16), 16)
            rule_payload['sequence'] = "{0:0{1}x}".format(vehicle.seq_counter, 8)
            rule_payload['rsvd'] = "00"
            rule_payload['unused'] = "0000"


            send_payload['sig_string'] = (rule_payload['prio'] + rule_payload['mask'] + rule_payload['id_xform']
                                            + rule_payload['data_xform'] + rule_payload['rsvd'] + rule_payload['filt']
                                            + rule_payload['data_operand'] + rule_payload['id_operand'] 
                                            + rule_payload['sequence'] + rule_payload['unused'])

            send_payload['hmac_sig'] = hmac.new(bytearray(str(fw_key)), msg=bytearray(send_payload['sig_string'].decode("hex")), digestmod=hashlib.sha256).hexdigest()

            payload_array.append(send_payload)

            #Can possibly drag out the save to outside the for loop for better performance and have local variable 
            #counter for sequence increment
            vehicle.seq_counter = vehicle.seq_counter + 1
            vehicle.save()

        except Exception as e:
            rul_obj = getattr(package, 'prio_'+str(hex(prio_num)))
            rule_payload = {}
            send_payload = {}
            rule_payload['prio'] = "{0:0{1}x}".format(prio_num,2)
            rule_payload['mask'] = "{0:0{1}x}".format(0, 8)
            rule_payload['filt'] = "{0:0{1}x}".format(0, 8)
            rule_payload['id_xform'] = "{0:0{1}x}".format(0, 1)
            rule_payload['data_xform'] = "{0:0{1}x}".format(0, 1)
            rule_payload['id_operand'] = "{0:0{1}x}".format(0, 8)
            rule_payload['data_operand'] = "{0:0{1}x}".format(0, 16)
            rule_payload['sequence'] = "{0:0{1}x}".format(vehicle.seq_counter, 8)
            rule_payload['rsvd'] = "00"
            rule_payload['unused'] = "0000"

            send_payload['sig_string'] = (rule_payload['prio'] + rule_payload['mask'] + rule_payload['id_xform']
                                            + rule_payload['data_xform'] + rule_payload['rsvd'] + rule_payload['filt']
                                            + rule_payload['data_operand'] + rule_payload['id_operand']
                                            + rule_payload['sequence'] + rule_payload['unused'])

            send_payload['hmac_sig'] = hmac.new(bytearray(str(fw_key)), msg=bytearray(send_payload['sig_string'].decode("hex")), digestmod=hashlib.sha256).hexdigest()

            payload_array.append(send_payload)
            vehicle.seq_counter = vehicle.seq_counter + 1
            vehicle.save()

    # notify remote of pending file transfer
    transaction_id += 1
    try:
        rvi_server.message(calling_service = rvi_service_id,
                           service_name = dst_url + rvi_service_id + '/package_acceptor',
                           transaction_id = str(transaction_id),
                           timeout = int(retry.get_timeout_epoch()),
                           # parameters = [{ u'package': package_name },
                           #               { u'payload': payload_array },
                           #               { u'num_prio': settings.RVI_CANFW_NUM_PRIO},
                           #              ])
                           parameters = {u'package':package_name, u'payload':payload_array,u'num_prio':settings.RVI_CANFW_NUM_PRIO}
                           )
    
    except Exception as e:
        logger.error('%s: Cannot send request: %s', retry, e)
        set_status(retry, can_fw.models.Status.FAILED)
        return False
    
    logger.info('%s: Notified remote of pending file transfer.', retry)
    
    # done
    set_status(retry, can_fw.models.Status.SUCCESS)
    logger.info('%s: Completed Update.', retry)
    return True
