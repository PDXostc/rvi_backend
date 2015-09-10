"""
Copyright (C) 2014, Jaguar Land Rover
This program is licensed under the terms and conditions of the
Mozilla Public License, version 2.0.  The full text of the 
Mozilla Public License is at https://www.mozilla.org/MPL/2.0/
Maintainer: Rudolf Streif (rstreif@jaguarlandrover.com) 
"""

"""
Author = David Thiriez
Invoke services via the cloud.
"""


from django.conf import settings
import os, threading, base64, json
import time, jsonrpclib
from urlparse import urlparse
import Queue
from rvijsonrpc import RVIJSONRPCServer
from django.conf import settings

from django.contrib.auth.models import User
from vehicles.models import Vehicle

import __init__
from __init__ import __RVI_LOGGER__ as rvi_logger


# globals
package_queue = Queue.Queue()
SERVER_NAME = "Invoke Service Server: "
transaction_id = 0

# Log Invoked Service Callback Server
class InvokeServicesServer(threading.Thread):
    """
    RPC server thread responding to Remote callbacks from the RVI framework.
    i.e. record service request that occur at the vehicle/RasPi
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
        self.localServer.register_function(log_invoked_service, self.service_id + "/service")

        # register services with RVI framework
        result = self.service_edge.register_service(service = self.service_id+'/service',
                                               network_address = self.callback_url)
        rvi_logger.info(SERVER_NAME + 'Registration: %s', result['service'])

    def run(self):
        self.localServer.serve_forever()

    def shutdown(self):
        self.localServer.shutdown()


# Callback functions
def log_invoked_service(username, vehicleVIN, service, latitude, longitude):
    rvi_logger.info(SERVER_NAME + 'Create new remote request: '
                    'username: %s\n'
                    'vehicleVIN: %s\n'
                    'service: %s\n'
                    'latitude: %s\n'
                    'longitude: %s\n'
                    , username, vehicleVIN, service, latitude, longitude)

    t1 = threading.Thread(target=thread_invoke_service, args=(
        username,
        vehicleVIN,
        service,
        latitude,
        longitude,
    ))
    t1.start()

    return {u'status': 0}


# Support (thread) functions
def thread_invoke_service(username, vehicleVIN, service, latitude, longitude):
    try:
        validate_invoke_service(username, vehicleVIN, service, latitude, longitude)
    except Exception:
        rvi_logger.exception(SERVER_NAME + 'Received data did not pass validation')

    send_invoked_service(username, vehicleVIN, service, latitude, longitude)
    rvi_logger.info(SERVER_NAME + 'Sent invoked service: %s', service)


# Support functions
def validate_invoke_service(username, vehicleVIN, service, latitude, longitude):
    try:
        user = User.objects.get(username=username)
        vehicle = Vehicle.objects.get(veh_vin=vehicleVIN)
    except User.DoesNotExist:
        rvi_logger.error(SERVER_NAME + 'username does not exist: %s', username)
        raise
    except Vehicle.DoesNotExist:
        rvi_logger.error(SERVER_NAME + 'VIN does not exist: %s', vehicleVIN)
        raise
    except Exception as e:
        rvi_logger.error(SERVER_NAME + 'Generic Error: %s', e)
        raise

    return True

def send_invoked_service(username, vehicleVIN, service, latitude, longitude):
    """
    Response for .../backend/dm/cert_requestall
    This provides all certificates by vehicle VIN and Device UUID
    """

    rvi_logger.info('%s: Sending all Remotes by VIN.', vehicleVIN)

    global transaction_id

    # get settings
    # service edge url
    try:
        rvi_service_url = settings.RVI_SERVICE_EDGE_URL
    except NameError:
        rvi_logger.error('%s: RVI_SERVICE_EDGE_URL not defined. Check settings!', vehicleVIN)
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
        rvi_logger.error('%s: Cannot read server key: %s', vehicleVIN, e)
        return False

    # establish outgoing RVI service edge connection
    rvi_server = None
    rvi_logger.info('%s: Establishing RVI service edge connection: %s', vehicleVIN, rvi_service_url)
    try:
        rvi_server = jsonrpclib.Server(rvi_service_url)
    except Exception as e:
        rvi_logger.error('%s: Cannot connect to RVI service edge: %s', vehicleVIN, e)
        return False
    # TODO JSONRPC is throwing an error for the log below, ProtocolError: (-32700, u'json error')
    # Commented out log message due to error mentioned above. However, the server connection still appears to work
    # logger.info('%s: Established connection to RVI Service Edge: %s', vehicleVIN, rvi_server)

    # notify remote of pending file transfer
    try:
        rvi_server.message(calling_service = rvi_service_id,
                       service_name = 'jlr.com/bt/stoffe/'+service,
                       transaction_id = str(transaction_id),
                       timeout = int(time.time()) + 5000,
                       parameters = [{
                                        u'username': username,
                                        u'vehicleVIN': vehicleVIN,
                                        u'latitude': latitude,
                                        u'longitude': longitude,
                                     },
                                    ])
    except Exception as e:
        rvi_logger.error('%s: Cannot connect to RVI service edge: %s', service, e)
        return False

    rvi_logger.info('%s: Sent command to bt stoffe.', service)
    return True

def boolean_to_string(boolean_value):
    if boolean_value:
        return 'True'
    else:
        return 'False'