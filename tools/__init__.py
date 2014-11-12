"""
Copyright (C) 2014, Jaguar Land Rover

This program is licensed under the terms and conditions of the
Mozilla Public License, version 2.0.  The full text of the 
Mozilla Public License is at https://www.mozilla.org/MPL/2.0/

Maintainer: Rudolf Streif (rstreif@jaguarlandrover.com) 
"""

"""
Initialize tools package.
"""

import sys, os, logging
import logging.config
import django
from django.conf import settings


# The backend server daemon depends on the Django ORM and uses settings
# from DJANGO_SETTINGS_MODULE. Append the relative path to the web
# backend to the Python search path for modules.
sys.path.append('../web')

# set the default Django settings module
# set the default Django settings module
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
django.setup()

# setup logging
logging.config.dictConfig(settings.LOGGING)
# use tools logger for general logging
__TOOLS_LOGGER__ = logging.getLogger('tools')


