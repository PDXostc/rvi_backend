"""
Copyright (C) 2014, Jaguar Land Rover

This program is licensed under the terms and conditions of the
Mozilla Public License, version 2.0.  The full text of the 
Mozilla Public License is at https://www.mozilla.org/MPL/2.0/

Rudolf Streif (rstreif@jaguarlandrover.com) 
"""

from django.db import models
from django.contrib.auth.models import User
 
class Account(models.Model):
    """
    Add user account to a model.
    """
    account = models.ForeignKey(User, editable=True)
    class Meta:
        abstract = True
 
