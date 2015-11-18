"""
Copyright (C) 2014, Jaguar Land Rover

This program is licensed under the terms and conditions of the
Mozilla Public License, version 2.0.  The full text of the 
Mozilla Public License is at https://www.mozilla.org/MPL/2.0/

Maintainer: Rudolf Streif (rstreif@jaguarlandrover.com) 
"""

"""
Initialize server package.
"""

import sys, os, logging
import logging.config
import django
from django.conf import settings


# The backend server daemon depends on the Django ORM and uses settings
# from DJANGO_SETTINGS_MODULE. Append the relative path to the web
# backend to the Python search path for modules.
sys.path.append('..')
sys.path.append('../web')

# set the default Django settings module
# set the default Django settings module
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings.local'
django.setup()

# setup logging
logging.config.dictConfig(settings.LOGGING)
# use RVI logger for general logging
__RVI_LOGGER__ = logging.getLogger('rvi')
# use SOTA logger for SOTA logging
__SOTA_LOGGER__ = logging.getLogger('rvi.sota')
# use Agent logger for DA logging
__DA_LOGGER__ = logging.getLogger('rvi.da')

