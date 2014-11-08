"""
Copyright (C) 2014, Jaguar Land Rover

This program is licensed under the terms and conditions of the
Mozilla Public License, version 2.0.  The full text of the 
Mozilla Public License is at https://www.mozilla.org/MPL/2.0/

Maintainer: Rudolf Streif (rstreif@jaguarlandrover.com) 
"""

from django.db import models
from sota.models import Retry


# Models for Logging

class DBLogEntry(models.Model):
    """
    Abstract base class for database logging
    Logging data clases need to be derived from this class
    """
    time = models.DateTimeField('Timestamp', auto_now_add=True)
    level = models.CharField('Level', max_length=10)
    message = models.TextField('Message')

    class Meta:
        abstract = True
 

class GeneralLog(DBLogEntry):
    """
    General log entry
    """
    class Meta:
        verbose_name = 'General Log'
        verbose_name_plural = 'General Log'
 

class SotaLog(DBLogEntry):
    """
    Software Over The Air (SOTA) Logging
    This class adds the foreign key 'retry' so that the log messages
    are associated with a particular SOTA run.
    To work correctly the first parameter passed to a log function
    must be a sota.models.Retry object e.g.
    logger.info("Log message: %s", retry)
    """
    retry = models.ForeignKey(Retry, verbose_name='Retry')
    class Meta:
        verbose_name = 'SOTA Log'
        verbose_name_plural = 'SOTA Log'
