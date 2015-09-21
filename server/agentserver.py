"""
Copyright (C) 2014, Jaguar Land Rover

This program is licensed under the terms and conditions of the
Mozilla Public License, version 2.0.  The full text of the 
Mozilla Public License is at https://www.mozilla.org/MPL/2.0/

Maintainer: Rudolf Streif (rstreif@jaguarlandrover.com) 
Author: Anson Fan

Dynamic Agents Transfer Server
"""

import os, threading, base64
import time
from urlparse import urlparse
import Queue
from rvijsonrpc import RVIJSONRPCServer

import __init__
from __init__ import __RVI_LOGGER__ as rvi_logger
from __init__ import __Agent_LOGGER__ as dynamicagents_logger
import dynamicagents.models

# globals
package_queue = Queue.Queue()


# Agent Callback Server
class AgentCallbackServer(threading.Thread):
    """
    RPC server thread responding to Agent callbacks from the RVI framework
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
        self.localServer.register_function(initiate_download, self.service_id + "/initiate_download")
        self.localServer.register_function(cancel_download, self.service_id + "/cancel_download")
        self.localServer.register_function(download_complete, self.service_id + "/download_complete")
        
        # register services with RVI framework
        result = self.service_edge.register_service(service = self.service_id+'/initiate_download',
                                               network_address = self.callback_url)
        rvi_logger.info('Agent Service Registration: Initiate download service name: %s', result['service'])
        result = self.service_edge.register_service(service = self.service_id+'/cancel_download',
                                               network_address = self.callback_url)
        rvi_logger.info('Agent Service Registration: Cancel download service name: %s', result['service'])
        result = self.service_edge.register_service(service = self.service_id+'/download_complete',
                                               network_address = self.callback_url)
        rvi_logger.info('Agent Service Registration: Download complete service name: %s', result['service'])

    def run(self):
        self.localServer.serve_forever()
        
    def shutdown(self):
        self.localServer.shutdown()
 
        
# Callback functions
def initiate_download(package, destination, retry):
    rvi_logger.info('Agent Callback Server: Initiate download request: retry %s - %s to %s.', retry, package, destination)
    package_queue.put([package, destination, retry])
    return {u'status': 0}

def cancel_download(retry):
    rvi_logger.info('Agent Callback Server: Cancel download request: retry: %s.', retry)
    retry_obj = None
    update_obj = None
    try:
        retry_obj = dynamicagents.models.Retry.objects.filter(pk=retry)[0]
        update_obj = retry_obj.ret_update
    except:
         rvi_logger.error('Agent Callback Server: Cancel downlaod request: Cannot access database object: %s', retry)
         return {u'status': 0}
    retry_obj.set_status(dynamicagents.models.Status.REJECTED)
    update_obj.set_status(dynamicagents.models.Status.REJECTED)
    dynamicagents_logger.info('Agent Callback Server: Cancel download request: %s.', retry_obj)
    return {u'status': 0}
    
def download_complete(status, retry):
    rvi_logger.info('Agent Callback Server: Download complete: retry: %s, status: %s.', retry, status)
    retry_obj = None
    update_obj = None
    try:
        retry_obj = dynamicagents.models.Retry.objects.filter(pk=retry)[0]
        update_obj = retry_obj.ret_update
    except:
         rvi_logger.error('Agent Callback Server: Download complete: Cannot access database object: %s', retry)
         return {u'status': 0}
    if int(status) == 0:
        retry_obj.set_status(dynamicagents.models.Status.SUCCESS)
        update_obj.set_status(dynamicagents.models.Status.SUCCESS)
    else:
        retry_obj.set_status(dynamicagents.models.Status.FAILED)
        update_obj.set_status(dynamicagents.models.Status.FAILED)
    dynamicagents_logger.info('Agent Callback Server: Download complete: retry: %s, status: %s.', retry_obj, status)
    return {u'status': 0}
    

# Agent Transmission Server
class AgentTransmissionServer(threading.Thread):
    """
    File transmission server thread. When a file download request was received from
    a client via initiate_download message it will be dipatched to the queue package_queue.
    This thread blocks on the package_queue until an entry is posted to the queue. Then
    it will start pushing the file to the client via the RVI framework.
    """
    
    def __init__(self, service_edge, service_id='/dynamicagents', chunk_size=65536):
        threading.Thread.__init__(self)
        self.service_edge = service_edge
        self.service_id = service_id
        self.chunk_size = chunk_size
        self.transaction_id = 0
        
    def shutdown(self):
        self._Thread__stop()
        
    def run(self):
        while True:
            [package, destination, retry] = package_queue.get()
            rvi_logger.info('Agent Transmission Server: Sending package %s to %s', package, destination)

            # accessing database objects
            retry_obj = None
            update_obj = None
            package_obj = None
            try:
                retry_obj = dynamicagents.models.Retry.objects.filter(pk=retry)[0]
                update_obj = retry_obj.ret_update
                package_obj = update_obj.upd_package
            except Exception as e:
                rvi_logger.error('Agent Transmission Server: Cannot access database object: %s, Error: %s', retry, e)
                continue

            try:
                f = open(package_obj.pac_file.path)
            except Exception as e:
                dynamicagents_logger.error('Agent Transmission Server: %s: Cannot open file: %s', retry_obj, package_obj.pac_file.path)
                retry_obj.set_status(dynamicagents.models.Status.FAILED)
                update_obj.set_status(dynamicagents.models.Status.FAILED)
                continue
 
            retry_obj.set_status(dynamicagents.models.Status.RUNNING)
            update_obj.set_status(dynamicagents.models.Status.RUNNING)


            f_stat = os.stat(package_obj.pac_file.path)

            self.transaction_id += 1
            self.service_edge.message(calling_service = self.service_id,
                               service_name = destination + "/start",
                               transaction_id = str(self.transaction_id),
                               timeout = int(retry_obj.get_timeout_epoch()),
                               parameters = [{ u'package': package,
                                               u'chunk_size': self.chunk_size,
                                               u'total_size': f_stat.st_size
                                           }])

            index = 0
            while True:
                msg =  f.read(self.chunk_size)
                if msg == "":
                    break
                dynamicagents_logger.debug('Agent Transmission Server: %s: Sending package: %s, chunk: %d, message size: %s', retry_obj, package, index, len(msg))
                self.transaction_id += 1
                self.service_edge.message(calling_service = self.service_id,
                                   service_name = destination + "/chunk",
                                   transaction_id = str(self.transaction_id),
                                   timeout = int(retry_obj.get_timeout_epoch()),
                                   parameters = [
                                       { u'index': index },
                                       { u'msg': base64.b64encode(msg) }])
                time.sleep(0.05)
                index += 1

            f.close()
            
            time.sleep(1.0)

            dynamicagents_logger.info('Agent Transmission Server: %s: Finishing package: %s', retry_obj, package)            
            self.transaction_id += 1
            self.service_edge.message(calling_service = self.service_id,
                               service_name = destination + "/finish",
                               transaction_id = str(self.transaction_id),
                               timeout = int(retry_obj.get_timeout_epoch()),
                               parameters = [ { u'dummy': 0}])


