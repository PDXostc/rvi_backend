"""
Copyright (C) 2014, Jaguar Land Rover
This program is licensed under the terms and conditions of the
Mozilla Public License, version 2.0.  The full text of the 
Mozilla Public License is at https://www.mozilla.org/MPL/2.0/
Maintainer: Rudolf Streif (rstreif@jaguarlandrover.com)
Author: David Thiriez (david.thiriez@p3-group.com)
Device Management / Remote services.
"""

import os, threading, base64
from dateutil import parser, tz
from urlparse import urlparse
import Queue
from rvijsonrpc import RVIJSONRPCServer
import json
import pytz, uuid

import __init__
from __init__ import __RVI_LOGGER__ as rvi_logger

from devices.tasks import send_remote, send_all_requested_remotes

from devices.models import Device, Remote
from vehicles.models import Vehicle

# globals
package_queue = Queue.Queue()
SERVER_NAME = "Backend Device Management Server: "

# Certificate Services Callback Server
class DeviceManagementServer(threading.Thread):
    """
    RPC server thread responding to Remote callbacks from the RVI framework.
    i.e. create certificate and update certificate requests from the mobile app
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
        self.localServer.register_function(create_remote, self.service_id + "/cert_create")
        self.localServer.register_function(modify_remote, self.service_id + "/cert_modify")
        self.localServer.register_function(requestall_remote, self.service_id + "/cert_requestall")

        # register services with RVI framework
        result = self.service_edge.register_service(service = self.service_id+'/cert_create',
                                               network_address = self.callback_url)
        rvi_logger.info(SERVER_NAME + 'Registration: '
                        'Create service name: %s', result['service'])

        result = self.service_edge.register_service(service = self.service_id+'/cert_modify',
                                               network_address = self.callback_url)
        rvi_logger.info(SERVER_NAME + 'Registration: '
                        'Modify service name: %s', result['service'])

        result = self.service_edge.register_service(service = self.service_id+'/cert_requestall',
                                               network_address = self.callback_url)
        rvi_logger.info(SERVER_NAME + 'Registration: '
                        'Retrieve all existing service name: %s', result['service'])

    def run(self):
        self.localServer.serve_forever()

    def shutdown(self):
        self.localServer.shutdown()


# Callback functions
def create_remote(username, vehicleVIN, authorizedServices, validFrom, validTo):
    rvi_logger.info(SERVER_NAME + 'Remote (Certificate) create request: \n'
                    'username: %s\n'
                    'vehicleVIN: %s\n'
                    'authorizedServices: %s\n'
                    'validFrom: %s\n'
                    'validTo: %s',
                    username, vehicleVIN, authorizedServices, validFrom, validTo)
    try:
        remote = validate_create_remote(username, vehicleVIN, authorizedServices, validFrom, validTo)
    except Exception:
        rvi_logger.exception(SERVER_NAME + 'Received data did not pass validation')
        return {u'status': 0}

    t1 = threading.Thread(target=thread_create_remote, args=(remote,))
    t1.start()

    return {u'status': 0}


def modify_remote(certid, authorizedServices, validFrom, validTo):
    rvi_logger.info(SERVER_NAME + 'Remote (Certificate) modify request: \n'
                    'certid: %s\n'
                    'authorizedServices: %s\n'
                    'validFrom: %s\n'
                    'validTo: %s',
                    certid, authorizedServices, validFrom, validTo)

    try:
        remote = validate_modify_remote(certid, authorizedServices, validFrom, validTo)
    except Exception:
        rvi_logger.exception(SERVER_NAME + 'Received data did not pass validation')
        return {u'status': 0}

    t1 = threading.Thread(target=thread_modify_remote, args=(remote,))
    t1.start()

    return {u'status': 0}


def requestall_remote(vehicleVIN, mobileUUID):
    rvi_logger.info(SERVER_NAME + 'Remote (Certificate) request to send all by VIN: \n'
                    'vehicleVIN: %s\n'
                    'mobileUUID: %s',
                    vehicleVIN, mobileUUID)

    try:
        validate_requestall_remote(vehicleVIN, mobileUUID)
    except Exception:
        rvi_logger.exception(SERVER_NAME + 'Received data did not pass validation')
        return {u'status': 0}

    t1 = threading.Thread(target=thread_requestall_remote, args=(vehicleVIN, mobileUUID,))
    t1.start()

    return {u'status': 0}


# Support (thread) functions
def thread_create_remote(remote):
    if Remote.objects.filter(rem_name = remote.rem_name).exists():
        rvi_logger.warning(SERVER_NAME + 'Deleting existing remote, %s', remote.get_name())
        Remote.objects.filter(rem_name = remote.rem_name).delete()

    remote.save()

    rvi_logger.info(SERVER_NAME + 'Remote created')

    result = send_remote(remote)
    if result:
        rvi_logger.info('Successfully Sent Remote: %s', remote.get_name())
    else:
        rvi_logger.error('Failed Sending Remote: %s', remote.get_name())


def thread_modify_remote(remote):
    remote.save(update_fields=[
        'rem_validfrom',
        'rem_validto',
        'rem_lock',
        'rem_engine',
        'rem_trunk',
        'rem_windows',
        'rem_lights',
        'rem_hazard',
        'rem_horn'
    ])
    rvi_logger.info(SERVER_NAME + 'Remote updated')

    result = send_remote(remote)

    if result:
        rvi_logger.info('Sending Remote: %s - successful', remote.get_name())
    else:
        rvi_logger.error('Sending Remote: %s - failed', remote.get_name())

    # Pseudo revoke. If all authorized services false, delete remote
    if remote.rem_lock == remote.rem_engine == False:
        rvi_logger.warning(SERVER_NAME + 'Deleting remote, %s', remote.get_name())
        Remote.objects.filter(rem_name = remote.rem_name).delete()


def thread_requestall_remote(vehicleVIN, mobileUUID):
    send_all_requested_remotes(vehicleVIN, mobileUUID)


# Validation functions
def validate_create_remote(username, vehicleVIN, authorizedServices, validFrom, validTo):
    try:
        device = Device.objects.get(dev_owner=username)
        vehicle = Vehicle.objects.get(veh_vin=vehicleVIN)
        parsed_data = json.dumps(authorizedServices)
        json_authorizedServices = json.loads(parsed_data)
        lock = parse_true_or_false((json_authorizedServices[0])[u'lock'])
        start = parse_true_or_false((json_authorizedServices[1])[u'start'])
        trunk = parse_true_or_false((json_authorizedServices[2])[u'trunk'])
        windows = parse_true_or_false((json_authorizedServices[3])[u'windows'])
        lights = parse_true_or_false((json_authorizedServices[4])[u'lights'])
        hazard = parse_true_or_false((json_authorizedServices[5])[u'hazard'])
        horn = parse_true_or_false((json_authorizedServices[6])[u'horn'])
        validFrom = parser.parse(str(validFrom).replace('T', ' ').replace('0Z',' +0000'))
        validTo = parser.parse(str(validTo).replace('T', ' ').replace('0Z',' +0000'))

    except Device.DoesNotExist:
        rvi_logger.error(SERVER_NAME + 'username does not exist: %s', username)
        raise
    except Vehicle.DoesNotExist:
        rvi_logger.error(SERVER_NAME + ' VIN does not exist: %s', vehicleVIN)
        raise
    except Exception as e:
        rvi_logger.error(SERVER_NAME + 'Generic Error: %s', e)
        raise

    return Remote(
        rem_name = 'remote_' + str(username),
        rem_device = device,
        rem_vehicle = vehicle,
        rem_validfrom = validFrom,
        rem_validto = validTo,
        rem_lock = lock,
        rem_engine = start,
        rem_trunk = trunk,
        rem_windows = windows,
        rem_lights = lights,
        rem_hazard = hazard,
        rem_horn = horn,
        rem_uuid = str(uuid.uuid4())
    )


def validate_modify_remote(certid, authorizedServices, validFrom, validTo):
    try:
        remote = Remote.objects.get(rem_uuid=certid)
        parsed_data = json.dumps(authorizedServices)
        json_authorizedServices = json.loads(parsed_data)
        lock = parse_true_or_false((json_authorizedServices[0])[u'lock'])
        start = parse_true_or_false((json_authorizedServices[1])[u'start'])
        trunk = parse_true_or_false((json_authorizedServices[2])[u'trunk'])
        windows = parse_true_or_false((json_authorizedServices[3])[u'windows'])
        lights = parse_true_or_false((json_authorizedServices[4])[u'lights'])
        hazard = parse_true_or_false((json_authorizedServices[5])[u'hazard'])
        horn = parse_true_or_false((json_authorizedServices[6])[u'horn'])

        validFrom = parser.parse(
            str(validFrom).replace('T', ' ').replace('0Z',' +0000')
        )
        validTo = parser.parse(
            str(validTo).replace('T', ' ').replace('0Z',' +0000')
        )
    except Remote.DoesNotExist:
        rvi_logger.error(SERVER_NAME + 'remote does not exist: %s', certid)
        raise
    except Exception as e:
        rvi_logger.error(SERVER_NAME + 'Generic Error: %s', e)
        raise

    remote.rem_validfrom = validFrom
    remote.rem_validto = validTo
    remote.rem_lock = lock
    remote.rem_engine = start
    remote.rem_trunk = trunk
    remote.rem_windows = windows
    remote.rem_lights = lights
    remote.rem_hazard = hazard
    remote.rem_horn = horn

    return remote


def validate_requestall_remote(vehicleVIN, mobileUUID):
    try:
        Vehicle.objects.get(veh_vin=vehicleVIN)
        Device.objects.get(dev_uuid=mobileUUID)
    except Vehicle.DoesNotExist:
        rvi_logger.error(SERVER_NAME + 'VIN does not exist: %s', vehicleVIN)
        raise
    except Device.DoesNotExist:
        rvi_logger.error(SERVER_NAME + 'Device does not exist: %s', mobileUUID)
        raise
    except Exception as e:
        rvi_logger.error(SERVER_NAME + 'Generic Error: %s', e)
        raise

    return True


# Support functions
def parse_true_or_false(service):
    if service == u'true':
        return True
    else:
        return False