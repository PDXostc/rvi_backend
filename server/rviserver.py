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

from util.daemon import Daemon

from server.sotaserver import SOTACallbackServer, SOTATransmissionServer
from server.trackingserver import TrackingCallbackServer


import __init__
from __init__ import __RVI_LOGGER__ as rvi_logger
from __init__ import __SOTA_LOGGER__ as sota_logger

import sota.models

def get_setting(name, default=None):
    try:
        value = getattr(settings, name, default)
    except AttributeError:
        rvi_logger.error('RVI Server: %s not defined. Check settings!', name)
        sys.exit(1)
    return value
        

def get_settings():
        # get settings from configuration
        # service edge url
        conf = {}
        conf['SERVICE_EDGE_URL']  = get_setting("RVI_SERVICE_EDGE_URL")
        conf['MEDIA_ROOT']        = get_setting("MEDIA_ROOT", ".")

        conf['SOTA_ENABLE']       = get_setting("RVI_SOTA_ENABLE", "True")
        conf['SOTA_CALLBACK_URL'] = get_setting("RVI_SOTA_CALLBACK_URL")
        conf['SOTA_SERVICE_ID']   = get_setting("RVI_SOTA_SERVICE_ID", "/sota")
        conf['SOTA_CHUNK_SIZE']   = int(get_setting("RVI_SOTA_CHUNK_SIZE", "131072"))

        conf['TRACKING_ENABLE']       = get_setting("RVI_TRACKING_ENABLE", "True")
        conf['TRACKING_CALLBACK_URL'] = get_setting("RVI_TRACKING_CALLBACK_URL")
        conf['TRACKING_SERVICE_ID']   = get_setting("RVI_TRACKING_SERVICE_ID", "/logging")

        return conf


class RVIServer(Daemon):
    """
    """
    rvi_service_edge = None
    sota_cb_server = None
    sota_tx_server = None
    tracking_cb_server = None
    
    def cleanup(self, *args):
        rvi_logger.info('RVI Server: Caught signal: %d. Shutting down...', args[0])
        if self.sota_cb_server:
            self.sota_cb_server.shutdown()
        if self.sota_tx_server:
            self.sota_tx_server.shutdown()
        if self.tracking_cb_server:
            self.tracking_cb_server.shutdown()
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
        if conf['SOTA_ENABLE'] == 'True':
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
        if conf['TRACKING_ENABLE'] == 'True':
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

        # catch signals for proper shutdown
        for sig in (SIGABRT, SIGTERM, SIGINT):
            signal(sig, self.cleanup)

        # main execution loop
        while True:
            try:
                time.sleep(10)
                # If we are idle too long the database server may
                # close the connection on us, ping the server to check if
                # the connection is still up.
                if (connection.connection is not None):
                    if (connection.is_usable() == True): 
                        rvi_logger.debug('RVI Server: Database connection is up.')
                    else:
                        rvi_logger.error('RVI Server: Database connection is down.')
                        connection.close()
                else:    
                    rvi_logger.error('RVI Server: Database connection is closed.')
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
            




