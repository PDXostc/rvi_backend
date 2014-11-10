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

from daemon import Daemon

from sotaserver import SOTACallbackServer, SOTATransmissionServer


import __init__
from __init__ import __RVI_LOGGER__ as rvi_logger
from __init__ import __SOTA_LOGGER__ as sota_logger

import sota.models





class RVIServer(Daemon):
    """
    """
    rvi_service_edge = None
    sota_cb_server = None
    sota_tx_server = None
    
    def cleanup(self, *args):
        rvi_logger.info('RVI Server: Caught signal: %d. Shutting down...', args[0])
        if self.sota_cb_server:
            self.sota_cb_server.shutdown()
        if self.sota_tx_server:
            self.sota_tx_server.shutdown()
        sys.exit(0)


    def run(self):
        # Execution starts here
        rvi_logger.info('RVI Server: Starting...')

        # get settings from configuration
        # service edge url
        try:
            rvi_url = settings.RVI_SERVICE_EDGE_URL
        except NameError:
            rvi_logger.error('RVI Server: RVI_SERVICE_EDGE_URL not defined. Check settings!')
            sys.exit(1)
        # chunk size
        try:
            rvi_chunk_size = settings.RVI_SOTA_CHUNK_SIZE
            rvi_chunk_size = int(rvi_chunk_size)
        except NameError:
            rvi_chunk_size = 128*1024
        # SOTA service url
        try:
            rvi_callback_url = settings.RVI_SOTA_CALLBACK_URL
        except NameError:
            rvi_logger.error('RVI Server: RVI_SOTA_CALLBACK_URL not defined. Check settings!')
            sys.exit(1)
        # SOTA service id
        try:
            rvi_service_id = settings.RVI_SOTA_SERVICE_ID
        except NameError:
            rvi_service_id = '/sota'
        # root directory for files
        try:
            media_root = settings.MEDIA_ROOT
        except NameError:
            media_root = '.'

        rvi_logger.info('RVI Server: Configuration: ' + 
            'BASE_DIR: '              + settings.BASE_DIR + ', ' +
            'RVI_SERVICE_EDGE_URL: '  + rvi_url + ', ' +
            'RVI_SOTA_CALLBACK_URL: ' + rvi_callback_url + ', ' +
            'RVI_SOTA_SERVICE_ID: '   + rvi_service_id + ', ' +
            'RVI_SOTA_CHUNK_SIZE: '   + str(rvi_chunk_size) + ', ' +
            'MEDIA_ROOT: '            + media_root
            )

        # setup RVI Service Edge
        rvi_logger.info('RVI Server: Setting up outbound connection to RVI Service Edge at %s', rvi_url)
        self.rvi_service_edge = jsonrpclib.Server(rvi_url)

        # start the SOTA callback server
        try:
            rvi_logger.info('RVI Server: Starting SOTA Callback Server on %s with service id %s.', rvi_callback_url, rvi_service_id)
            self.sota_cb_server = SOTACallbackServer(self.rvi_service_edge, rvi_service_id, rvi_callback_url)
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
            self.sota_tx_server = SOTATransmissionServer(self.rvi_service_edge, rvi_service_id, rvi_chunk_size)
            self.sota_tx_server.start()
            rvi_logger.info('RVI Server: SOTA Transmission Server started.')
        except Exception as e:
            rvi_logger.error('RVI Server: Cannot start SOTA Transmission Server: %s', e)
            sys.exit(1)
    
        # wait for SOTA transmission server to come up    
        time.sleep(0.5)

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
                    if (connection.is_usable()): 
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
            




