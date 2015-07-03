"""
Copyright (C) 2014, Jaguar Land Rover

This program is licensed under the terms and conditions of the
Mozilla Public License, version 2.0.  The full text of the 
Mozilla Public License is at https://www.mozilla.org/MPL/2.0/

Maintainer: Rudolf Streif (rstreif@jaguarlandrover.com) 
"""

"""
GPS Data Collector

Message Queue Sink that publishes messages to a Kafka message queue.
"""

import __init__
import os
import threading
import base64
import time
import Queue
import json

from urlparse import urlparse
from rvijsonrpc import RVIJSONRPCServer
from kafka import KafkaClient, SimpleProducer
from __init__ import __RVI_LOGGER__ as logger

from server.utils import get_settings

class MQSinkServer(threading.Thread):
    """
    Publish data report to message queue
    """
    def __init__(self, service_edge, callback_url, service_id):
        threading.Thread.__init__(self)

        self.service_edge = service_edge
        self.service_id = service_id
        self.callback_url = callback_url
        url = urlparse(self.callback_url)
        self.localServer = RVIJSONRPCServer(addr=((url.hostname, url.port)), logRequests=False)
        self.register_services()

        
    def register_services(self):
        # register callback functions with RPC server
        self.localServer.register_function(report, self.service_id + "/report")

        # register services with RVI framework
        result = self.service_edge.register_service(service = self.service_id+'/report',
                                               network_address = self.callback_url)
        logger.info('Tracking Service Registration: Report service name: %s', result['service'])

    def run(self):
        self.localServer.serve_forever()

    def shutdown(self):
        self.localServer.shutdown()
    
            
def report(timestamp, vin, data):
        """
        Log the location record
        """
        conf = get_settings()
        
        kafka = None
        logger.info('Kafka MQ Server: Report Request: Time: %s, VIN: %s, Data: %s.', timestamp, vin, data)
        payload = {}
        payload['timestamp'] = timestamp
        payload['vin'] = vin
        payload['data'] = data
        # Connect to Kafka Message Queue Server
       
        try:
            kafka = KafkaClient(conf['TRACKING_MQ_URL'])
        except:
            logger.error("%s: Kafka Message Queue Server unavailable:", conf['TRACKING_MQ_URL'])
            kafka = None
            return False
                
        producer = SimpleProducer(kafka)
        producer.send_messages(conf['TRACKING_MQ_TOPIC'], json.dumps(payload))
        logger.info("%s: Report data published to message queue.", conf['TRACKING_MQ_URL'])
        return True


