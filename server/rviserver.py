"""
Copyright (C) 2014, Jaguar Land Rover

This program is licensed under the terms and conditions of the
Mozilla Public License, version 2.0.  The full text of the 
Mozilla Public License is at https://www.mozilla.org/MPL/2.0/

Maintainer: Rudolf Streif (rstreif@jaguarlandrover.com) 
"""

"""
Backend daemon that connects to RVI, receives, dispatches and processes
incoming messages from vehicles.
"""

import sys, os, logging, jsonrpclib
import time
from signal import *
from urlparse import urlparse
import Queue

import django
from django.conf import settings
from django.db import connection

import __init__

from util.daemon import Daemon
from server.sotaserver import SOTACallbackServer, SOTATransmissionServer
from server.trackingserver import TrackingCallbackServer
from server.certificateservicesserver import CertificateServicesServer
from server.loginvokedserviceserver import LogInvokedServicesServer
from server.mqsinkserver import MQSinkServer
from server.hbaseserver import HBaseServer
from server.utils import get_settings

from __init__ import __RVI_LOGGER__ as rvi_logger
from __init__ import __SOTA_LOGGER__ as sota_logger

import sota.models



class RVIServer(Daemon):
    """
    """
    rvi_service_edge = None
    sota_cb_server = None
    sota_tx_server = None
    tracking_cb_server = None
    certificate_services_cb = None
    mq_sink_server = None
    hbase_server = None
    def cleanup(self, *args):
        rvi_logger.info('RVI Server: Caught signal: %d. Shutting down...', args[0])
        if self.sota_cb_server:
            self.sota_cb_server.shutdown()
        if self.sota_tx_server:
            self.sota_tx_server.shutdown()
        if self.tracking_cb_server:
            self.tracking_cb_server.shutdown()
        if self.certificate_services_cb:
            self.certificate_services_cb.shutdown()
        if self.mq_sink_server:
            self.mq_sink_server.shutdown()
        if self.hbase_server:
            self.hbase_server.shutdown()
        sys.exit(0)


    def run(self):
        # Execution starts here
        rvi_logger.info('RVI Server: Starting...')

        conf = get_settings()

        rvi_logger.info('RVI Server: General Configuration: ' + 
            'RVI_SERVICE_EDGE_URL: '  + conf['SERVICE_EDGE_URL']  + ', ' +
            'MEDIA_ROOT: '            + conf['MEDIA_ROOT']
            )

        # setup RVI Service Edge
        rvi_logger.info('RVI Server: Setting up outbound connection to RVI Service Edge at %s', conf['SERVICE_EDGE_URL'])
        self.rvi_service_edge = jsonrpclib.Server(conf['SERVICE_EDGE_URL'])

        # SOTA Startup
        if conf['SOTA_ENABLE'] == True:
            # log SOTA configuration
            rvi_logger.info('RVI Server: SOTA Configuration: ' + 
                'RVI_SOTA_CALLBACK_URL: ' + conf['SOTA_CALLBACK_URL'] + ', ' +
                'RVI_SOTA_SERVICE_ID: '   + conf['SOTA_SERVICE_ID']   + ', ' +
                'RVI_SOTA_CHUNK_SIZE: '   + str(conf['SOTA_CHUNK_SIZE'])
                )
            # start the SOTA callback server
            try:
                rvi_logger.info('RVI Server: Starting SOTA Callback Server on %s with service id %s.', conf['SOTA_CALLBACK_URL'], conf['SOTA_SERVICE_ID'])
                self.sota_cb_server = SOTACallbackServer(self.rvi_service_edge, conf['SOTA_CALLBACK_URL'], conf['SOTA_SERVICE_ID'])
                self.sota_cb_server.start()
                rvi_logger.info('RVI Server: SOTA Callback Server started.')
            except Exception as e:
                rvi_logger.error('RVI Server: Cannot start SOTA Callback Server: %s', e)
                sys.exit(1)

            # wait for SOTA callback server to come up    
            time.sleep(0.5)

            # start SOTA Transmission Server
            try:
                rvi_logger.info('RVI Server: Starting SOTA Transmission Server.')
                self.sota_tx_server = SOTATransmissionServer(self.rvi_service_edge, conf['SOTA_SERVICE_ID'], conf['SOTA_CHUNK_SIZE'])
                self.sota_tx_server.start()
                rvi_logger.info('RVI Server: SOTA Transmission Server started.')
            except Exception as e:
                rvi_logger.error('RVI Server: Cannot start SOTA Transmission Server: %s', e)
                sys.exit(1)
    
            # wait for SOTA transmission server to come up    
            time.sleep(0.5)
            
        # Tracking Startup
        if conf['TRACKING_ENABLE'] == True:
            # log Tracking configuration
            rvi_logger.info('RVI Server: Tracking Configuration: ' + 
                'RVI_TRACKING_CALLBACK_URL: ' + conf['TRACKING_CALLBACK_URL'] + ', ' +
                'RVI_TRACKING_SERVICE_ID: '   + conf['TRACKING_SERVICE_ID']
                )
            # start the Tracking callback server
            try:
                rvi_logger.info('RVI Server: Starting Tracking Callback Server on %s with service id %s.', conf['TRACKING_CALLBACK_URL'], conf['TRACKING_SERVICE_ID'])
                self.tracking_cb_server = TrackingCallbackServer(self.rvi_service_edge, conf['TRACKING_CALLBACK_URL'], conf['TRACKING_SERVICE_ID'])
                self.tracking_cb_server.start()
                rvi_logger.info('RVI Server: Tracking Callback Server started.')
            except Exception as e:
                rvi_logger.error('RVI Server: Cannot start Tracking Callback Server: %s', e)
                sys.exit(1)

            # wait for SOTA callback server to come up    
            time.sleep(0.5)

        else:
            rvi_logger.info('RVI Server: Tracking not enabled')


        # Remote (certificate) Services Startup
        if conf['CERTIFICATE_SERVICES_ENABLE'] == True:
            # log Remote (certificate) Services configuration
            rvi_logger.info('RVI Server: Remote (certificate) Services Configuration: ' +
                'RVI_CERTIFICATE_SERVICES_CALLBACK_URL: ' + conf['CERTIFICATE_SERVICES_CALLBACK_URL'] + ', ' +
                'RVI_CERTIFICATE_SERVICES_SERVICE_ID: '   + conf['CERTIFICATE_SERVICES_CALLBACK_ID']
                )
            # start the Remote (certificate) Services callback server
            try:
                rvi_logger.info(
                    'RVI Server: Starting Remote (certificate) Services Server on %s with service id %s.',
                    conf['CERTIFICATE_SERVICES_CALLBACK_URL'],
                    conf['CERTIFICATE_SERVICES_CALLBACK_ID']
                )
                self.certificate_services_cb = CertificateServicesServer(
                    self.rvi_service_edge,
                    conf['CERTIFICATE_SERVICES_CALLBACK_URL'],
                    conf['CERTIFICATE_SERVICES_CALLBACK_ID']
                )
                self.certificate_services_cb.start()
                rvi_logger.info('RVI Server: Remote (certificate) Services Callback Server started.')
            except Exception as e:
                rvi_logger.error('RVI Server: Cannot start Remote (certificate) Services Callback Server: %s', e)
                sys.exit(1)

            # wait for Remote (certificate) Services callback server to come up
            time.sleep(0.5)

        else:
            rvi_logger.info('RVI Server: Remote (certificate) Services not enabled')


        # Log Invoked Service Service Startup
        if conf['LOG_INVOKED_SERVICES_ENABLE'] == True:
            # log Log Invoked Services Service configuration
            rvi_logger.info('RVI Server: Log Invoked Services Service Configuration: ' +
                'RVI_LOG_INVOKED_SERVICES_CALLBACK_URL: ' + conf['LOG_INVOKED_SERVICES_CALLBACK_URL'] + ', ' +
                'RVI_LOG_INVOKED_SERVICES_CALLBACK_ID: '   + conf['LOG_INVOKED_SERVICES_CALLBACK_ID']
                )
            # start the Log Invoked Services Service callback server
            try:
                rvi_logger.info(
                    'RVI Server: Starting Log Invoked Services Service Server on %s with service id %s.',
                    conf['LOG_INVOKED_SERVICES_CALLBACK_URL'],
                    conf['LOG_INVOKED_SERVICES_CALLBACK_ID']
                )
                self.certificate_services_cb = LogInvokedServicesServer(
                    self.rvi_service_edge,
                    conf['LOG_INVOKED_SERVICES_CALLBACK_URL'],
                    conf['LOG_INVOKED_SERVICES_CALLBACK_ID']
                )
                self.certificate_services_cb.start()
                rvi_logger.info('RVI Server: Log Invoked Services Service Callback Server started.')
            except Exception as e:
                rvi_logger.error('RVI Server: Cannot start Log Invoked Services Service Callback Server: %s', e)
                sys.exit(1)

            # wait for Log Invoked Services Service callback server to come up
            time.sleep(0.5)

        else:
            rvi_logger.info('RVI Server: Log Invoked Services Service not enabled')


        # Publish to Kafka Message Queue
        if conf['TRACKING_MQ_PUBLISH'] == True:
            #log kafka configuration
            rvi_logger.info('RVI Server: Publishing to Kafka Message Queue: ' + conf['TRACKING_MQ_URL'] + ' , with topic: ' + conf['TRACKING_MQ_TOPIC'])

            #Start the Kafka message queue forwarding server
            try:
                rvi_logger.info('%s: Publishing to message queue enabled.', self.__class__.__name__)
                self.mq_sink_server = MQSinkServer(self.rvi_service_edge, conf['TRACKING_CALLBACK_URL'], conf['TRACKING_SERVICE_ID'])
                self.mq_sink_server.start()
                rvi_logger.info('RVI Server: Message Queue Server started.')
            except Exception as e:
                rvi_logger.error('RVI Server: Cannot start Message Queue Server: %s', e)
                sys.exit(1)

        else:
            rvi_logger.info('RVI Server: MQ Publish not enabled')

        # Save message Queue contents into HBase
        if conf['TRACKING_MQ_HBASE'] == True:
            rvi_logger.info('RVI Server: Saving to HBase: ' + conf['TRACKING_MQ_HBASE_URL'])
           
            #Start HBase Server thread
            try:
                rvi_logger.info('%s: Saving messages to HBase enabled.', self.__class__.__name__)
                self.hbase_server = HBaseServer(conf['TRACKING_MQ_URL'],conf['TRACKING_MQ_TOPIC'],conf['TRACKING_MQ_HBASE_URL'], conf['TRACKING_MQ_HBASE_PORT'], conf['TRACKING_MQ_HBASE_TABLE']) 
                self.hbase_server.start()
                rvi_logger.info('RVI Server: Kafka -> HBase consumer started.')
            except Exception as e:
                rvi_logger.error('RVI Server: Cannot start HBase Server: %s', e)
                sys.exit(1)
        else:
            rvi_logger.info('RVI Server: HBase server storage not enabled')


        # catch signals for proper shutdown
        for sig in (SIGABRT, SIGTERM, SIGINT):
            signal(sig, self.cleanup)

        # main execution loop
        timeout = conf['DB_CLOSE_TIMEOUT']
        while True:
            try:
                time.sleep(conf['DB_PING_INTERVAL'])
                # If we are idle too long the database server may
                # close the connection on us, ping the server to check if
                # the connection is still up.
                if (connection.connection is not None):
                    if (connection.is_usable() == True): 
                        rvi_logger.debug('RVI Server: Database connection is up.')
                        # Close connection if open longer than the timeout
                        timeout -= conf['DB_PING_INTERVAL']
                        if (timeout <= 0):
                            connection.close()
                            timeout = conf['DB_CLOSE_TIMEOUT']
                            rvi_logger.info('RVI Server: Idle Timeout: closed database connection.')
                    else:
                        rvi_logger.error('RVI Server: Database connection is down.')
                        connection.close()
                elif (conf['TRACKING_MQ_PUBLISH'] == True and conf['TRACKING_ENABLE'] == False):
                    pass
                else:    
                    rvi_logger.error('RVI Server: Database connection is closed.')
                    # As long as the connection is closed reset the timeout
                    timeout = conf['DB_CLOSE_TIMEOUT']
                    
            except KeyboardInterrupt:
                print ('\n')
                break



def usage():
    print "RVI Server: Usage: %s foreground|start|stop|restart" % sys.argv[0]        
        
if __name__ == "__main__":
    pid_file = '/var/run/' + os.path.splitext(__file__)[0] + '.pid'
    rvi_server = None
    if len(sys.argv) == 3:
        pid_file = sys.argv[2]
    rvi_server = RVIServer(pid_file, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null')
    if len(sys.argv) >= 2:
        if sys.argv[1] in ('foreground', 'fg'):
            # in foreground we also log to the console
            rvi_logger.addHandler(logging._handlers['console'])
            rvi_server.run()
        elif sys.argv[1] in ('start', 'st'):
            rvi_server.start()
        elif sys.argv[1] in ('stop', 'sp'):
            rvi_server.stop()
        elif sys.argv[1] in ('restart', 're'):
            rvi_server.restart()
        else:
            print "RVI Server: Unknown command."
            usage()
            sys.exit(2)
    else:
        usage()
        sys.exit(2)
            




