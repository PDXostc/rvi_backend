"""
Copyright (C) 2014, Jaguar Land Rover
This program is licensed under the terms and conditions of the
Mozilla Public License, version 2.0.  The full text of the 
Mozilla Public License is at https://www.mozilla.org/MPL/2.0/
Maintainer: Rudolf Streif (rstreif@jaguarlandrover.com) 
"""

"""
Author = David Thiriez
Device Management / Remote (certificate) services.
"""

import os, threading, base64
import time
import datetime
from dateutil import parser
from devices.models import Device, Remote
from vehicles.models import Vehicle
from devices.tasks import send_remote
from django.contrib.auth.models import User

from urlparse import urlparse
import Queue
from rvijsonrpc import RVIJSONRPCServer
import json
import __init__
from __init__ import __RVI_LOGGER__ as rvi_logger


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
        self.localServer.register_function(requestall_remote, self.service_id + "/cert_requesteall")

        # register services with RVI framework
        result = self.service_edge.register_service(service = self.service_id+'/cert_create',
                                               network_address = self.callback_url)
        rvi_logger.info(SERVER_NAME + 'Registration: '
                        'Create service name: %s', result['service'])

        result = self.service_edge.register_service(service = self.service_id+'/cert_modify',
                                               network_address = self.callback_url)
        rvi_logger.info(SERVER_NAME + 'Registration: '
                        'Modify service name: %s', result['service'])

        result = self.service_edge.register_service(service = self.service_id+'/cert_requesteall',
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

    rvi_logger.info(SERVER_NAME + 'Attempting to create remote')
    if not Remote.objects.filter(rem_name = remote.rem_name).exists():
        remote.save()
    else:
        rvi_logger.exception(SERVER_NAME + 'Remote with name %s already exists', remote.get_name())
        return {u'status': 0}

    result = send_remote(remote)
    if result:
        rvi_logger.info('Successfully Sent Remote: %s', remote.get_name())
    else:
        rvi_logger.error('Failed Sending Remote: %s', remote.get_name())

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

    rvi_logger.info(SERVER_NAME + 'Attempting to update remote')
    remote.save(update_fields=['rem_validfrom', 'rem_validto', 'rem_lock', 'rem_engine'])

    result = send_remote(remote)

    if result:
        rvi_logger.info('Sending Remote: %s - successful', remote.get_name())
    else:
        rvi_logger.error('Sending Remote: %s - failed', remote.get_name())

    return {u'status': 0}


def requestall_remote(vehicleVIN):
    rvi_logger.info(SERVER_NAME + 'Remote (Certificate) request to send all by VIN: \n'
                    'vehicleVIN: %s',
                    vehicleVIN)

    try:
        vehicle = validate_requestall_remote(vehicleVIN)
    except Exception:
        rvi_logger.exception(SERVER_NAME + 'Received data did not pass validation')
        return {u'status': 0}

    certificates = []
    for remote in Remote.objects.filter(rem_vehicle_id = vehicle.veh_key_id):

        mobile = remote.rem_device
        user = User.objects.get(id=mobile.account_id)

        certificate = {}
        certificate['certid'] = remote.rem_uuid
        certificate['username'] = user.username
        certificate['authorizedServices'] = {
            u'lock': remote.rem_lock,
            u'engine': remote.rem_engine,
            u'trunk': remote.rem_trunk,
            u'windows': remote.rem_windows,
            u'lights': remote.rem_lights,
            u'hazard': remote.rem_hazard,
            u'horn': remote.rem_horn
        }
        certificate['validFrom'] = str(remote.rem_validfrom)
        certificate['ValidTo'] = str(remote.rem_validto)
        rvi_logger.info("Tied to queried VIN %s: %s", vehicleVIN, certificate)

    return {u'status': 0}


# Support functions
def validate_create_remote(username, vehicleVIN, authorizedServices, validFrom, validTo):
    try:
        device = Device.objects.get(dev_owner=username)
        vehicle = Vehicle.objects.get(veh_vin=vehicleVIN)
        parsed_data = json.dumps(authorizedServices)
        services = json.loads(parsed_data)
        engine = services[u'start']
        lock = services[u'lock']
        validFrom = parser.parse(
            str(validFrom).replace('T', ' ').replace('Z','+00:00')
        )
        validTo = parser.parse(
            str(validTo).replace('T', ' ').replace('Z','+00:00')
        )
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
        rem_device_id = device.dev_key_id,
        rem_vehicle_id = vehicle.veh_key_id,
        rem_validfrom = validFrom,
        rem_validto = validTo,
        rem_lock = lock,
        rem_engine = engine
    )


def validate_modify_remote(certid, authorizedServices, validFrom, validTo):
    try:
        remote = Remote.objects.get(rem_uuid=certid)
        parsed_data = json.dumps(authorizedServices)
        services = json.loads(parsed_data)
        engine = int(services[u'start'] == u'true')
        lock = int(services[u'lock'] == u'true')
        validFrom = parser.parse(
            str(validFrom).replace('T', ' ').replace('Z','+00:00')
        )
        validTo = parser.parse(
            str(validTo).replace('T', ' ').replace('Z','+00:00')
        )
    except Remote.DoesNotExist:
        rvi_logger.error(SERVER_NAME + 'username does not exist: %s', username)
        raise
    except Exception as e:
        rvi_logger.error(SERVER_NAME + 'Generic Error: %s', e)
        raise

    remote.rem_validfrom = validFrom
    remote.rem_validto = validTo
    remote.rem_lock = lock
    remote.rem_engine = engine

    return remote


def validate_requestall_remote(vehicleVIN):
    try:
        vehicle = Vehicle.objects.get(veh_vin=vehicleVIN)
    except Vehicle.DoesNotExist:
        rvi_logger.error(SERVER_NAME + 'VIN does not exist: %s', vehicleVIN)
        raise
    except Exception as e:
        rvi_logger.error(SERVER_NAME + 'Generic Error: %s', e)
        raise

    return vehicle


def send_remote(remote):
    """
    Notify destination, typically a vehicle, of a pending software
    update.
    :param retry: sota.models.Retry object
    """

    logger.info('%s: Sending Remote.', remote)

    global transaction_id

    # get settings
    # service edge url
    try:
        rvi_service_url = settings.RVI_SERVICE_EDGE_URL
    except NameError:
        logger.error('%s: RVI_SERVICE_EDGE_URL not defined. Check settings!', remote)
        return False

    # DM service id
    try:
        rvi_service_id = settings.RVI_DM_SERVICE_ID
    except NameError:
        rvi_service_id = '/dm'

    # Signature algorithm
    try:
        alg = settings.RVI_BACKEND_ALG_SIG
    except NameError:
        alg = 'RS256'

    # Server Key
    try:
        keyfile = open(settings.RVI_BACKEND_KEYFILE, 'r')
        key = keyfile.read()
    except Exception as e:
        logger.error('%s: Cannot read server key: %s', remote, e)
        return False

    # Create and sign certificate
    try:
        cert = remote.encode_jwt(key, alg)
    except Exception as e:
        logger.error('%s: Cannot create and sign certificate: %s', remote, e)
        return False

    # establish outgoing RVI service edge connection
    rvi_server = None
    logger.info('%s: Establishing RVI service edge connection: %s', remote, rvi_service_url)
    try:
        rvi_server = jsonrpclib.Server(rvi_service_url)
    except Exception as e:
        logger.error('%s: Cannot connect to RVI service edge: %s', remote, e)
        return False
    logger.info('%s: Established connection to RVI Service Edge: %s', remote, rvi_server)

    # get destination info
    mobile = remote.rem_device
    dst_url = mobile.get_rvi_id()

    # get user info
    user = User.objects.get(id=mobile.account_id)
    vehicle = remote.rem_vehicle

    if vehicle.list_account() == user.username:
        user_type = 'owner'
    else:
        user_type = 'guest'

    if remote.rem_name == 'remote_videodemo_owner':
        user_type = 'owner'
    elif remote.rem_name == 'remote_videodemo_guest':
        user_type = 'guest'

    valid_from = str(remote.rem_validfrom).replace(' ', 'T').replace('+00:00', '')+'.000Z'
    valid_to = str(remote.rem_validto).replace(' ', 'T').replace('+00:00', '')+'.000Z'

    # notify remote of pending file transfer
    transaction_id += 1
    try:
        rvi_server.message(calling_service = rvi_service_id,
                       service_name = dst_url + rvi_service_id + '/cert_provision',
                       transaction_id = str(transaction_id),
                       timeout = int(time.time()) + 5000,
                       parameters = [{ u'certid': remote.rem_uuid },
                                     { u'certificate': cert },
                                     {
                                        u'username': user.username,
                                        u'userType': user_type,
                                        u'vehicleName': vehicle.veh_name,
                                        u'vehicleVIN': vehicle.veh_vin,
                                        u'validFrom': valid_from,
                                        u'validTo': valid_to,
                                        u'authorizedServices': {
                                            u'lock': remote.rem_lock,
                                            u'engine': remote.rem_engine,
                                            u'trunk': remote.rem_trunk,
                                            u'windows': remote.rem_windows,
                                            u'lights': remote.rem_lights,
                                            u'hazard': remote.rem_hazard,
                                            u'horn': remote.rem_horn
                                        },
                                        # TODO implement guest account retrieval
                                        u'guests': [
                                            u'arodriguez', u'bjamal'
                                        ]
                                     },
                                    ])
    except Exception as e:
        logger.error('%s: Cannot connect to RVI service edge: %s', remote, e)
        return False

    logger.info('%s: Sent Certificate.', remote)
    return True
