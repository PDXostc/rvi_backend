"""
Copyright (C) 2014, Jaguar Land Rover

This program is licensed under the terms and conditions of the
Mozilla Public License, version 2.0.  The full text of the 
Mozilla Public License is at https://www.mozilla.org/MPL/2.0/

Rudolf Streif (rstreif@jaguarlandrover.com) 
"""

from __future__ import absolute_import

import sys, os, logging, time, jsonrpclib, base64
import Queue

from urlparse import urlparse

from django.conf import settings

from django.contrib.auth.models import User, Group

# import devices.models
# from vehicles.models import Vehicle


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

    # get user info
    user = User.objects.get(id=mobile.account_id)
    vehicle = remote.rem_vehicle

    if vehicle.list_account() == user.username:
        user_type = 'owner'
    else:
        user_type = 'guest'

    if remote.rem_name == 'remote_videodemo_owner':
        user_type = 'owner'
    elif remote.rem_name == 'remote_videodemo_guest':
        user_type = 'guest'

    valid_from = str(remote.rem_validfrom).replace(' ', 'T').replace('+00:00', '')+'.000Z'
    valid_to = str(remote.rem_validto).replace(' ', 'T').replace('+00:00', '')+'.000Z'
 
    # notify remote of pending file transfer
    transaction_id += 1
    try:
        rvi_server.message(calling_service = rvi_service_id,
                       service_name = dst_url + rvi_service_id + '/cert_provision',
                       transaction_id = str(transaction_id),
                       timeout = int(time.time()) + 5000,
                       parameters = [{ u'certid': remote.rem_uuid },
                                     { u'certificate': cert },
                                     {
                                        u'username': user.username,
                                        u'userType': user_type,
                                        u'vehicleName': vehicle.veh_name,
                                        u'vehicleVIN': vehicle.veh_vin,
                                        u'validFrom': valid_from,
                                        u'validTo': valid_to,
                                        u'authorizedServices': {
                                            u'lock': remote.rem_lock,
                                            u'engine': remote.rem_engine,
                                            u'trunk': remote.rem_trunk,
                                            u'windows': remote.rem_windows,
                                            u'lights': remote.rem_lights,
                                            u'hazard': remote.rem_hazard,
                                            u'horn': remote.rem_horn
                                        },
                                        # TODO implement guest account retrieval
                                        u'guests': [
                                            u'arodriguez', u'bjamal'
                                        ]
                                     },
                                    ])
    except Exception as e:
        logger.error('%s: Cannot connect to RVI service edge: %s', remote, e)
        return False

    logger.info('%s: Sent Certificate.', remote)
    return True
