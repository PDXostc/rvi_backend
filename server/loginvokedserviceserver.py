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
from urlparse import urlparse
import Queue
from rvijsonrpc import RVIJSONRPCServer

import __init__
from __init__ import __RVI_LOGGER__ as rvi_logger


# globals
package_queue = Queue.Queue()


# Log Invoked Service Callback Server
class LogInvokedServicesServer(threading.Thread):
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
        self.localServer.register_function(log_invoked_service, self.service_id + "/report/serviceinvoked")

        # register services with RVI framework
        result = self.service_edge.register_service(service = self.service_id+'/report/serviceinvoked',
                                               network_address = self.callback_url)
        rvi_logger.info('Log Invoked Services Service Registration: '
                        'Create new Log Invoked Services service name: %s', result['service'])

    def run(self):
        self.localServer.serve_forever()

    def shutdown(self):
        self.localServer.shutdown()


# Callback functions
def log_invoked_service(username, vehicleVIN, latitude, longitude, timestamp):
    rvi_logger.info('Remote (Certificate) Server: Create new remote request: '
                    'username: %s\n'
                    'vehicleVIN: %s\n'
                    'latitude: %s\n'
                    'longitude: %s\n'
                    'timestamp: %s\n'
                    , username, vehicleVIN, latitude, longitude, timestamp)

    return {u'status': 0}