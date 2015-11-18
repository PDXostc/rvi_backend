"""
Copyright (C) 2014, Jaguar Land Rover

This program is licensed under the terms and conditions of the
Mozilla Public License, version 2.0.  The full text of the 
Mozilla Public License is at https://www.mozilla.org/MPL/2.0/
Maintainer: Rudolf Streif (rstreif@jaguarlandrover.com)
Modified by: David Thiriez (david.thiriez@p3-group.com)
"""

from __future__ import absolute_import

import sys, os, logging, time, jsonrpclib, base64
import Queue, json

from urlparse import urlparse

from django.db.models import Q
from django.conf import settings

from django.contrib.auth.models import User, Group

from devices.models import Device, Remote
from vehicles.models import Vehicle


# Logging setup
logger = logging.getLogger('rvi')

# Globals
transaction_id = 0


def send_remote(remote):
    """
    Notify destination, typically a vehicle, of a pending software
    update.
    :param retry: sota.models.Retry object
    """
    
    logger.info('%s: Sending Remote.', remote)

    global transaction_id
    
    # get settings
    # service edge url
    try:
        rvi_service_url = settings.RVI_SERVICE_EDGE_URL
    except NameError:
        logger.error('%s: RVI_SERVICE_EDGE_URL not defined. Check settings!', remote)
        return False

    # DM service id
    try:
        rvi_service_id = settings.RVI_DM_SERVICE_ID
    except NameError:
        rvi_service_id = '/dm'

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
        logger.error('%s: Cannot read server key: %s', remote, e)
        return False
        
    # Create and sign certificate
    try:
        cert = remote.encode_jwt(key, alg)
    except Exception as e:
        logger.error('%s: Cannot create and sign certificate: %s', remote, e)
        return False

    # establish outgoing RVI service edge connection
    rvi_server = None
    logger.info('%s: Establishing RVI service edge connection: %s', remote, rvi_service_url)
    try:
        rvi_server = jsonrpclib.Server(rvi_service_url)
    except Exception as e:
        logger.error('%s: Cannot connect to RVI service edge: %s', remote, e)
        return False
    logger.info('%s: Established connection to RVI Service Edge: %s', remote, rvi_server)
    
    # get destination info
    mobile = remote.rem_device
    dst_url = mobile.get_rvi_id()

    # notify remote of pending file transfer
    transaction_id += 1
    try:
        rvi_server.message(calling_service = rvi_service_id,
                       service_name = dst_url + rvi_service_id + '/cert_provision',
                       transaction_id = str(transaction_id),
                       timeout = int(time.time()) + 5000,
                       parameters = [{ u'certid': remote.rem_uuid },
                                     { u'certificate': cert },
                                    ])
    except Exception as e:
        logger.error('%s: Cannot connect to RVI service edge: %s', remote, e)
        return False

    logger.info('%s: Sent Certificate.', remote)

    '''
    Following successful send of cert_provision, cert_accountdetails is sent down to the same device (see below).
    Mobile app then parses this payload to render its UI.
    '''
    time.sleep(2)

    # get user info
    username = remote.rem_device.dev_owner
    vehicle = remote.rem_vehicle
    owner_username = vehicle.list_account()

    logger.info("comparing %s and %s", str(username), str(owner_username))
    if str(owner_username) == str(username):
        user_type = u'owner'
    else:
        user_type = u'guest'

    valid_from = unicode(remote.rem_validfrom).replace(' ', 'T').replace('+00:00', '')+'.000Z'
    valid_to = unicode(remote.rem_validto).replace(' ', 'T').replace('+00:00', '')+'.000Z'

    guests = User.objects.exclude(Q(username=owner_username) | Q(is_superuser=True))
    guests_dict = []
    for guest in guests:
        guests_dict.append(guest.username)

    '''
    if 'test_owner' in remote.rem_name:
        user_type = u'owner'
    elif 'test_guest' in remote.rem_name:
        user_type = u'guest'
    '''

    try:
        rvi_server.message(calling_service = rvi_service_id,
                       service_name = dst_url + rvi_service_id + '/cert_accountdetails',
                       transaction_id = str(transaction_id),
                       timeout = int(time.time()) + 5000,
                       parameters = [{
                                        u'username': username,
                                        u'userType': user_type,
                                        u'vehicleName': vehicle.veh_name,
                                        u'vehicleVIN': vehicle.veh_vin,
                                        u'validFrom': valid_from,
                                        u'validTo': valid_to,
                                        u'authorizedServices': {
                                            u'lock': unicode(remote.rem_lock),
                                            u'engine': unicode(remote.rem_engine),
                                            u'trunk': unicode(remote.rem_trunk),
                                            u'windows': unicode(remote.rem_windows),
                                            u'lights': unicode(remote.rem_lights),
                                            u'hazard': unicode(remote.rem_hazard),
                                            u'horn': unicode(remote.rem_horn)
                                        },
                                        # TODO implement how guests are tied to a vehicle
                                        # Presently, all users other than the owner are retrieved
                                        u'guests': guests_dict
                                     },
                                    ])
    except Exception as e:
        logger.error('%s: Cannot connect to RVI service edge: %s', remote, e)
        return False
    logger.info('%s: Sent Account Details.', username)
    return True


def send_all_requested_remotes(vehicleVIN, deviceUUID):
    """
    Response for .../backend/dm/cert_requestall
    This provides all certificates by vehicle VIN and Device UUID
    """

    logger.info('%s: Sending all Remotes by VIN.', vehicleVIN)

    global transaction_id

    # get settings
    # service edge url
    try:
        rvi_service_url = settings.RVI_SERVICE_EDGE_URL
    except NameError:
        logger.error('%s: RVI_SERVICE_EDGE_URL not defined. Check settings!', vehicleVIN)
        return False

    # DM service id
    try:
        rvi_service_id = settings.RVI_DM_SERVICE_ID
    except NameError:
        rvi_service_id = '/dm'

    # establish outgoing RVI service edge connection
    rvi_server = None
    logger.info('%s: Establishing RVI service edge connection: %s', vehicleVIN, rvi_service_url)
    try:
        rvi_server = jsonrpclib.Server(rvi_service_url)
    except Exception as e:
        logger.error('%s: Cannot connect to RVI service edge: %s', vehicleVIN, e)
        return False
    # TODO JSONRPC is throwing an error for the log below, ProtocolError: (-32700, u'json error')
    # Commented out log message due to error mentioned above. However, the server connection still appears to work
    # logger.info('%s: Established connection to RVI Service Edge: %s', vehicleVIN, rvi_server)

    # get destination info
    owner_mobile = Device.objects.get(dev_uuid=deviceUUID)
    dst_url = owner_mobile.get_rvi_id()

    # get user info
    owner_vehicle = Vehicle.objects.get(veh_vin=vehicleVIN)

    certificates = []
    for remote in Remote.objects.filter(rem_vehicle=owner_vehicle).exclude(rem_device=owner_mobile):

        mobile = remote.rem_device
        username = remote.rem_device.dev_owner

        valid_from = unicode(remote.rem_validfrom).replace(' ', 'T').replace('+00:00', '')+'.000Z'
        valid_to = unicode(remote.rem_validto).replace(' ', 'T').replace('+00:00', '')+'.000Z'

        certificate = {}
        certificate[u'certid'] = remote.rem_uuid
        certificate[u'username'] = username
        certificate[u'authorizedServices'] = {
            u'lock': unicode(remote.rem_lock),
            u'engine': unicode(remote.rem_engine),
            u'trunk': unicode(remote.rem_trunk),
            u'windows': unicode(remote.rem_windows),
            u'lights': unicode(remote.rem_lights),
            u'hazard': unicode(remote.rem_hazard),
            u'horn': unicode(remote.rem_horn)
        }
        certificate[u'validFrom'] = valid_from
        certificate[u'validTo'] = valid_to
        certificates.append(certificate)

    message = {}
    message[u'certificates'] = certificates

    try:
        rvi_server.message(calling_service = rvi_service_id,
                       service_name = dst_url + rvi_service_id + '/cert_response',
                       transaction_id = str(transaction_id),
                       timeout = int(time.time()) + 5000,
                       parameters = json.dumps(message))
    except Exception as e:
        logger.error('%s: Cannot connect to RVI service edge: %s', remote, e)
        return False

    logger.info('%s: Sent list of all remotes.', remote)
    return True
