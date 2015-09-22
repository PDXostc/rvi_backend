"""
Copyright (C) 2014, Jaguar Land Rover
This program is licensed under the terms and conditions of the
Mozilla Public License, version 2.0.  The full text of the 
Mozilla Public License is at https://www.mozilla.org/MPL/2.0/
Maintainer: Rudolf Streif (rstreif@jaguarlandrover.com) 
"""

"""
Author = David Thiriez
Log invoked services.
"""

from django.conf import settings
import os, threading, base64, json
import time, jsonrpclib
from urlparse import urlparse
import Queue
from rvijsonrpc import RVIJSONRPCServer
from dateutil import parser
import requests

from django.contrib.auth.models import User
from vehicles.models import Vehicle
from servicehistory.models import ServiceInvokedHistory
from devices.models import Device
from server.utils import get_setting

import urllib2
from bs4 import BeautifulSoup

import __init__
from __init__ import __RVI_LOGGER__ as rvi_logger


# globals
package_queue = Queue.Queue()
SERVER_NAME = "Log Invoked Service Server: "
transaction_id = 0


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
        rvi_logger.info(SERVER_NAME + 'Registration: %s', result['service'])

    def run(self):
        self.localServer.serve_forever()

    def shutdown(self):
        self.localServer.shutdown()


# Callback functions
def log_invoked_service(username, vehicleVIN, service, latitude, longitude, timestamp):
    rvi_logger.info(SERVER_NAME + 'Create new remote request: \n'
                    'username: %s\n'
                    'vehicleVIN: %s\n'
                    'service: %s\n'
                    'latitude: %s\n'
                    'longitude: %s\n'
                    'timestamp: %s'
                    , username, vehicleVIN, service, latitude, longitude, timestamp)

    t1 = threading.Thread(target=thread_log_invoked_service, args=(
        username,
        vehicleVIN,
        service,
        latitude,
        longitude,
        timestamp,
    ))
    t1.start()

    return {u'status': 0}


# Support (thread) functions
def thread_log_invoked_service(username, vehicleVIN, service, latitude, longitude, timestamp):
    try:
        serviceinvoked = validate_log_invoked_service(username, vehicleVIN, service, latitude, longitude, timestamp)
    except Exception:
        rvi_logger.exception(SERVER_NAME + 'Received data did not pass validation')

    serviceinvoked.save()
    rvi_logger.info(SERVER_NAME + 'Saved log of the following service invoked record: %s', serviceinvoked)

    vehicle = Vehicle.objects.get(veh_vin = vehicleVIN)
    owner_username = vehicle.list_account()

    if owner_username != username:
        send_service_invoked_by_guest(owner_username, username, vehicleVIN, service)


# Support functions
def validate_log_invoked_service(username, vehicleVIN, service, latitude, longitude, timestamp):
    try:
        user = User.objects.get(username=username)
        vehicle = Vehicle.objects.get(veh_vin=vehicleVIN)
        service_timestamp = parser.parse(
            str(timestamp).replace('T', ' ').replace('Z','+00:00')
        )
        address = reverse_geocode(latitude, longitude)
        '''
        # Reverse geocoding via screen scraping
        url = 'http://nominatim.openstreetmap.org/search.php?q=' + str(latitude) + '%2C+' + str(longitude)
        page = urllib2.urlopen(url)
        soup = BeautifulSoup(page, 'html.parser')
        address = soup.find_all("span", class_="name")[0].get_text()
        '''
    except User.DoesNotExist:
        rvi_logger.error(SERVER_NAME + 'username does not exist: %s', username)
        raise
    except Vehicle.DoesNotExist:
        rvi_logger.error(SERVER_NAME + 'VIN does not exist: %s', vehicleVIN)
        raise
    except Exception as e:
        rvi_logger.error(SERVER_NAME + 'Generic Error: %s', e)
        raise
    '''
    except urllib2.URLError, e:
        rvi_logger.error(SERVER_NAME + 'Reverse Geocoding URLError: %s', e)
        raise
    except urllib2.HTTPError, e:
        rvi_logger.error(SERVER_NAME + 'Reverse Geocoding HTTPException: %s', e)
        raise
    '''


    return ServiceInvokedHistory(
        hist_user = user,
        hist_service = service,
        hist_latitude = latitude,
        hist_longitude = longitude,
        hist_address = address,
        hist_vehicle = vehicle,
        hist_timestamp = service_timestamp
    )


def send_service_invoked_by_guest(owner_username, guest_username, vehicleVIN, service):
    """
    Response for .../backend/logging/report/serviceinvoked
    Communicates to .../{UUID}/report/serviceinvokedbyguest
    This provides the owner phone a notification that a guest key has invoked a service
    """

    rvi_logger.info('send_service_invoked_by_guest %s: %s service executed by %s.', vehicleVIN, service, guest_username)

    global transaction_id

    # get settings
    # service edge url
    try:
        rvi_service_url = settings.RVI_SERVICE_EDGE_URL
    except NameError:
        rvi_logger.error('%s: RVI_SERVICE_EDGE_URL not defined. Check settings!', vehicleVIN)
        return False

    # DM service id
    rvi_service_id = '/report'

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

    # get destination info
    # TODO rely on account tied to phone instead of dev_owner field
    owner_device = Device.objects.get(dev_owner=owner_username)
    dst_url = owner_device.get_rvi_id()

    # TODO JSONRPC is throwing an error for the log below, ProtocolError: (-32700, u'json error')
    # Commented out log message due to error mentioned above. However, the server connection still appears to work
    # logger.info('%s: Established connection to RVI Service Edge: %s', vehicleVIN, rvi_server)

    # notify remote of pending file transfer
    try:
        rvi_server.message(calling_service = rvi_service_id,
                       service_name = dst_url + rvi_service_id + '/serviceinvokedbyguest',
                       transaction_id = str(transaction_id),
                       timeout = int(time.time()) + 5000,
                       parameters = [{
                                        u'username': guest_username,
                                        u'vehicleVIN': vehicleVIN,
                                        u'service': service,
                                     },
                                    ])
    except Exception as e:
        rvi_logger.error('%s: Cannot connect to RVI service edge: %s', service, e)
        return False

    rvi_logger.info('send_service_invoked_by_guest - %s by %s on %s. Owner notified.', service, guest_username, vehicleVIN)
    return True

def reverse_geocode(latitude, longitude):
    # Did the geocoding request comes from a device with a
    # location sensor? Must be either true or false.
    sensor = 'true'

    # Hit Google's reverse geocoder directly
    # NOTE: I *think* their terms state that you're supposed to
    # use google maps if you use their api for anything.

    base = "https://maps.googleapis.com/maps/api/geocode/json?"
    params = "latlng={lat},{lon}&sensor={sen}&key={key}".format(
        lat=latitude,
        lon=longitude,
        sen=sensor,
        key=get_setting("GOOGLE_API_KEY")
    )
    url = "{base}{params}".format(base=base, params=params)
    response = requests.get(url)

    # rvi_logger.info('Google Request: %s', url)
    rvi_logger.info('Google Response: %s', response.json)
    return response.json()['results'][0]['formatted_address']
