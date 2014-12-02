"""
Copyright (C) 2014, Jaguar Land Rover

This program is licensed under the terms and conditions of the
Mozilla Public License, version 2.0.  The full text of the 
Mozilla Public License is at https://www.mozilla.org/MPL/2.0/

Maintainer: Rudolf Streif (rstreif@jaguarlandrover.com) 
"""

"""
GPS Data Collector

This tool collects data from the gpsd daemon and stores it in the RVI Backend
database using the Django ORM.
"""

import sys
import getopt
import os
import time
import logging
import threading

import django
from django.conf import settings
from django.db import connection

from signal import *
from gps import *

from util.daemon import Daemon

import __init__
from __init__ import __TOOLS_LOGGER__ as logger

from vehicles.models import Vehicle
from tracking.models import Location

MY_NAME = "GPS Collector"

class GPSPoller(threading.Thread):
    
    def __init__(self):
        threading.Thread.__init__(self)
        self.session = gps(mode=WATCH_ENABLE)
        
    def shutdown(self):
        self._Thread__stop()
        
    def run(self):
        while True:
            self.session.next()


class GPSCollector(Daemon):
    """
    """
    
    
    def __init__(self, vehicle_name, interval, pidfile, nofix=False,
                 stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
        super(GPSCollector,self).__init__(pidfile, stdin, stdout, stderr)
        self.vehicle_name = vehicle_name
        self.interval = interval
        self.nofix = nofix
        self.last_speed = 1.0
        self.gps_poller = GPSPoller()

    def run(self):
        # get the vehicle record
        try:
            vehicle = Vehicle.objects.get(veh_name = self.vehicle_name)
        except:
            logger.error("%s: Vehicle '%s' does not exist in database. Add it first.", MY_NAME, self.vehicle_name)
            sys.exit(2)
            
        # start GPS polling thread
        self.gps_poller.start()

        # catch signals for proper shutdown
        for sig in (SIGABRT, SIGTERM, SIGINT):
            signal(sig, self.cleanup)

        # main execution loop
        while True:
            try:
                time.sleep(self.interval)
                # If we are idle too long the database server may
                # close the connection on us, ping the server to check if
                # the connection is still up.
                if (connection.connection is not None):
                    if (connection.is_usable()): 
                        logger.debug('%s: Database connection is up.', MY_NAME)
                    else:
                        logger.error('%s: Database connection is down.', MY_NAME)
                        connection.close()
                else:    
                    logger.error('%s: Database connection is closed.', MY_NAME)
                
                # process GPS data
                session = self.gps_poller.session
                if (session.fix.mode == MODE_NO_FIX) and not self.nofix:
                    logger.info("%s: Waiting for GPS to fix...", MY_NAME)
                    continue
                
                if not isnan(session.fix.time):
                    if (session.fix.speed < 0.1) and (self.last_speed < 0.1):
                        continue
                    self.last_speed = session.fix.speed
                    # if the time is valid the data record is valid
                    location = Location()
                    location.loc_vehicle = vehicle
                    location.loc_time = session.utc
                    location.loc_latitude = session.fix.latitude
                    location.loc_longitude = session.fix.longitude
                    if (session.fix.mode == MODE_3D):
                        location.loc_altitude = session.fix.altitude
                    location.loc_speed = session.fix.speed
                    location.loc_climb = session.fix.climb
                    location.loc_track = session.fix.track
                    location.save()
                    logger.info("%s: Valid location: %s", MY_NAME, location)
                else:
                    logger.debug("%s: Invalid location: %s", MY_NAME)
                    

            except KeyboardInterrupt:
                print ('\n')
                break

    def cleanup(self, *args):
        logger.info('%s: Caught signal: %d. Shutting down...', MY_NAME, args[0])
        if self.gps_poller:
            self.gps_poller.shutdown()
        sys.exit(0)




def usage():
    print "Usage: %s foreground|start|stop|restart -v <vehicle> [-i <interval] [-p <pidfile>]" % sys.argv[0]
        
if __name__ == "__main__":
    pid_file = '/var/run/' + os.path.splitext(__file__)[0] + '.pid'
    vehicle_name = None
    interval = 5
    gps_collector = None
    nofix = False
    
    try:
        opts, args = getopt.getopt(sys.argv[2:], "hi:fv:p:", ["vehicle=", "interval=", "pidfile="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    print opts
    for opt, arg in opts:
        if opt == '-h':
            usage()
            sys.exit(1)
        elif opt == '-f':
            nofix = True
        elif opt in ("-v", "-vehicle"):
            vehicle_name = arg
        elif opt in ("-i", "-interval"):
            interval = int(arg)
        elif opt in ("-p", "-pidfile"):
            pid_file = arg

    if vehicle_name is None:
        usage()
        print "Must provide vehicle"
        sys.exit(2)

    logger.info("%s: Logging GPS data for vehicle: %s", MY_NAME, vehicle_name)

    gps_collector = GPSCollector(vehicle_name, interval, pid_file, nofix, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null')

    if len(sys.argv) >= 2:
        if sys.argv[1] in ('foreground', 'fg'):
            gps_collector.run()
        elif sys.argv[1] in ('start', 'st'):
            gps_collector.start()
        elif sys.argv[1] in ('stop', 'sp'):
            gps_collector.stop()
        elif sys.argv[1] in ('restart', 're'):
            gps_collector.restart()
        else:
            print "%s: Unknown command." % sys.argv[0]
            usage()
            sys.exit(2)
    else:
        usage()
        sys.exit(2)
            

