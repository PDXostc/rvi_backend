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


# SOTA Callback Server
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
        self.localServer.register_function(create_remote, self.service_id + "/create_remote")
        self.localServer.register_function(modify_remote, self.service_id + "/modify_remote")

        # register services with RVI framework
        result_create_certificate = self.service_edge.register_service(service = self.service_id+'/create_remote',
                                               network_address = self.callback_url)
        rvi_logger.info('Remote (certificate) Service Registration: '
                        'Create new Remote (certificate) service name: %s', result_create_certificate['service'])

        result_modify_certificate = self.service_edge.register_service(service = self.service_id+'/modify_remote',
                                               network_address = self.callback_url)
        rvi_logger.info('Remote (certificate) Service Registration: '
                        'Modify existing Remote (certificate) service name: %s', result_modify_certificate['service'])

    def run(self):
        self.localServer.serve_forever()

    def shutdown(self):
        self.localServer.shutdown()


# Callback functions
def create_remote(result_create_certificate):
    rvi_logger.info('Remote (Certificate) Server: Create new remote request: result %s.', result_create_certificate)

    return {u'status': 0}


def modify_remote(result_modify_certificate):
    rvi_logger.info('Remote (Certificate) Server: Modify existing remote request: result %s.', result_modify_certificate)

    return {u'status': 0}