"""
Copyright (C) 2014, Jaguar Land Rover
This program is licensed under the terms and conditions of the
Mozilla Public License, version 2.0.  The full text of the 
Mozilla Public License is at https://www.mozilla.org/MPL/2.0/
Maintainer: Rudolf Streif (rstreif@jaguarlandrover.com) 
Author: David Thiriez (david.thiriez@p3-group.com)
Owner notification that a guest has invoked a service.
"""

from __future__ import absolute_import

import logging, time, jsonrpclib
import Queue

from django.conf import settings

from devices.models import Device, Remote


# Logging setup
logger = logging.getLogger('rvi')

# Globals
package_queue = Queue.Queue()
SERVER_NAME = "Log Invoked Service Server: "
transaction_id = 0


def send_service_invoked_by_guest(owner_username, guest_username, vehicleVIN, service):
    """
    Response for .../backend/logging/report/serviceinvoked
    Communicates to .../{UUID}/report/serviceinvokedbyguest
    This provides the owner phone a notification that a guest key has invoked a service
    """

    logger.info('send_service_invoked_by_guest %s: %s service executed by %s.', vehicleVIN, service, guest_username)

    global transaction_id

    # get settings
    # service edge url
    try:
        rvi_service_url = settings.RVI_SERVICE_EDGE_URL
    except NameError:
        logger.error('%s: RVI_SERVICE_EDGE_URL not defined. Check settings!', vehicleVIN)
        return False

    # Invoked by guest service id
    rvi_service_id = '/report'

    # establish outgoing RVI service edge connection
    rvi_server = None
    logger.info('%s: Establishing RVI service edge connection: %s', vehicleVIN, rvi_service_url)
    try:
        rvi_server = jsonrpclib.Server(rvi_service_url)
    except Exception as e:
        logger.error('%s: Cannot connect to RVI service edge: %s', vehicleVIN, e)
        return False

    # get destination info
    # TODO rely on account tied to phone instead of dev_owner field
    # Presently, all devices added via the admin portal need to have the dev_owner field manually set to the
    # account username they are tied to
    owner_device = Device.objects.get(dev_owner=owner_username)
    dst_url = owner_device.get_rvi_id()

    # TODO JSONRPC is throwing an error for the log below, ProtocolError: (-32700, u'json error')
    # Commented out log message due to error mentioned above. However, the server connection still appears to work
    # logger.info('%s: Established connection to RVI Service Edge: %s', vehicleVIN, rvi_server)

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
        logger.error('%s: Cannot connect to RVI service edge: %s', service, e)
        return False

    logger.info('send_service_invoked_by_guest - %s by %s on %s. Owner notified.', service, guest_username, vehicleVIN)
    return True
