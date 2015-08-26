"""
Copyright (C) 2014, Jaguar Land Rover
This program is licensed under the terms and conditions of the
Mozilla Public License, version 2.0.  The full text of the 
Mozilla Public License is at https://www.mozilla.org/MPL/2.0/
Maintainer: Rudolf Streif (rstreif@jaguarlandrover.com) 
"""

"""
Author = David Thiriez
Remote (certificate) services.
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


# Certificate Services Callback Server
class CertificateServicesServer(threading.Thread):
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
        rvi_logger.info('Remote (certificate) Service Registration: '
                        'Create new Remote (certificate) service name: %s', result['service'])

        result = self.service_edge.register_service(service = self.service_id+'/cert_modify',
                                               network_address = self.callback_url)
        rvi_logger.info('Remote (certificate) Service Registration: '
                        'Modify existing Remote (certificate) service name: %s', result['service'])

        result = self.service_edge.register_service(service = self.service_id+'/cert_requesteall',
                                               network_address = self.callback_url)
        rvi_logger.info('Remote (certificate) Service Registration: '
                        'Retrieve all existing Remote (certificate) service name: %s', result['service'])


    def run(self):
        self.localServer.serve_forever()

    def shutdown(self):
        self.localServer.shutdown()


# Callback functions
def create_remote(username, vehicleVIN, authorizedServices, validFrom, validTo):
    rvi_logger.info('Remote (Certificate) Server: Create new remote request: \n'
                    'username: %s\n'
                    'vehicleVIN: %s\n'
                    'authorizedServices: %s\n'
                    'validFrom: %s\n'
                    'validTo: %s',
                    username, vehicleVIN, authorizedServices, validFrom, validTo)

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
    except Exception as e:
        rvi_logger.error("Certificate Callback Server Error -- conversion: %s", e)
        return {u'status': 0}

    remote = Remote(
        rem_name = 'remote_'+str(username)+'_API',
        rem_device_id = device.dev_key_id,
        rem_vehicle_id = vehicle.veh_key_id,
        rem_validfrom = validFrom,
        rem_validto = validTo,
        rem_lock = lock,
        rem_engine = engine
    )
    if not Remote.objects.filter(rem_name = remote.rem_name).exists():
        try:
            rvi_logger.info('Attempting to create the following remote: %s', remote)
            remote.save()
        except Exception as e:
            rvi_logger.error("Certificate Callback Server Error -- creation: %s", e)
            return {u'status': 0}
    else:
        rvi_logger.info('Certificate Callback Server Error -- remote already exists: %s', remote.get_name())

    result = send_remote(remote)
    if result:
        rvi_logger.info('Sending Remote: %s - successful', remote.get_name())
    else:
        rvi_logger.error('Sending Remote: %s - failed', remote.get_name())

    return {u'status': 0}


def modify_remote(certid, authorizedServices, validFrom, validTo):
    rvi_logger.info('Remote (Certificate) Server: Modify existing remote request: \n'
                    'certid: %s\n'
                    'authorizedServices: %s\n'
                    'validFrom: %s\n'
                    'validTo: %s',
                    certid, authorizedServices, validFrom, validTo)
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
    except Exception as e:
        rvi_logger.error("Certificate Callback Server Error: %s", e)
        return {u'status': 0}

    remote.rem_validfrom = validFrom
    remote.rem_validto = validTo
    remote.rem_lock = lock
    remote.rem_engine = engine

    try:
        rvi_logger.info('Attempting to update the following remote: %s', remote)
        remote.save(update_fields=['rem_validfrom', 'rem_validto', 'rem_lock', 'rem_engine'])
    except Exception as e:
        rvi_logger.error("Certificate Callback Server Error -- update: %s", e)
        return {u'status': 0}


    result = send_remote(remote)
    if result:
        rvi_logger.info('Sending Remote: %s - successful', remote.get_name())
    else:
        rvi_logger.error('Sending Remote: %s - failed', remote.get_name())

    return {u'status': 0}


def requestall_remote(vehicleVIN):
    rvi_logger.info('Remote (Certificate) Server: request all Remotes tied to a VIN: \n'
                    'vehicleVIN: %s',
                    vehicleVIN)

    try:
        vehicle = Vehicle.objects.get(veh_vin=vehicleVIN)

    except Exception as e:
        rvi_logger.error("Certificate Callback Server Error: %s", e)
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