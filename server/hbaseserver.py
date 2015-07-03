"""
Version: 0.1
HBase code for our RVI stuff put whatever notices, legal stuff, maintainer, etc...

Takes messages from Kafka message queue and inserts into HBase
For time being code is not modular... will update to create a table settings file
for future modurization.

HBase Sink which takes messages from Kafka message queue and inserts into HBase
"""

import __init__

import os
import threading
import base64
import Queue
import json
import happybase

from __init__ import __RVI_LOGGER__ as logger
from kafka import KafkaClient, SimpleConsumer
from time import sleep

class HBaseServer(threading.Thread):
    """
    HBase thread that will continuously read from Kafka queue
    """

    def __init__(self, kafka_url, kafka_topic, hbase_url, hbase_thrift_port, hbase_table):
        threading.Thread.__init__(self)
        
        self.kafka = KafkaClient(kafka_url)
        self.cons = SimpleConsumer(self.kafka, None, kafka_topic)
        self.cons.seek(0,2)
        
        self.hbase_connect = happybase.Connection(hbase_url,hbase_thrift_port)
        self.car_table = self.hbase_connect.table(hbase_table)
        
        self.server_on_flag = True        
        self.m = None
        self.payload = None
        self.vin = None
        self.time = None
        self.data = None
        self.row_key = None
        self.count = 0

    def run(self):
        while self.server_on_flag:

            self.m = self.cons.get_message(block=False)
           
            if (self.m is not None):
                self.payload = json.loads(self.m.message.value)
                self.vin = str(self.payload['vin'])
                self.time = str(self.payload['timestamp'])
                self.data = str(self.payload['data'])
                
                self.row_key = self.vin+self.time
                try:
                    self.car_table.put(self.vin,{'user:mostrecent':self.time})
                    self.car_table.put(self.row_key,{'car:data':self.data})
                    self.count = self.count + 1
                    logger.info('HBase Server: key: %s, table: %s, car{data: %s}. Message number: %s', self.row_key, 'rvi', self.data, str(self.count))     
           
                except Exception as e:
                    logger.info('%s,Data Push into HBase unsuccessful...', e)

            else:
                sleep(1/5)

    def shutdown(self):
        self.server_on_flag = False
        logger.info('HBase Server shutting down...')




