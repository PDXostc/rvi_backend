"""
Copyright (C) 2014, Jaguar Land Rover

This program is licensed under the terms and conditions of the
Mozilla Public License, version 2.0.  The full text of the 
Mozilla Public License is at https://www.mozilla.org/MPL/2.0/

Maintainer: Rudolf Streif (rstreif@jaguarlandrover.com) 
"""

from logging import Handler
from django.utils import timezone
import json, datetime, random
 

class DBHandler(Handler,object):
    """
    This handler will add logs to a database model defined in settings.py
    If the log message (pre-format) is a json string, it will try to apply
    the array onto the log event object
    """

    model_name = None
    expiry = None
 
    def __init__(self, model="", expiry=0):
        super(DBHandler,self).__init__()
        self.model_name = model
        self.expiry = int(expiry)
 
    def emit(self,record):
        # big try block here to exit silently if exception occurred
        try:
            # instantiate the model
            model = self.get_model(self.model_name)

            # create the table entry for the log                
            log_entry = self.create_logentry(model, record)
 
            # test if msg is json and apply to log record object
            try:
                data = json.loads(record.msg)
                for key,value in data.items():
                    if hasattr(log_entry,key):
                        try:
                            setattr(log_entry,key,value)
                        except:
                            pass
            except:
                pass
 
            log_entry.save()

            # in 20% of time, check and delete expired logs
            if self.expiry and random.randint(1,5) == 1:
                model.objects.filter(time__lt = timezone.now() - datetime.timedelta(seconds=self.expiry)).delete()
        except:
            pass
 
    def get_model(self, name):
        try:
            names = name.split('.')
            mod = __import__('.'.join(names[:-1]), fromlist=names[-1:])
            return getattr(mod, names[-1])
        except:
            from dblog.models import GeneralLog as model
            return model
            
    def create_logentry(self, model, record):
        return model(level=record.levelname, message=self.format(record))


class SotaHandler(DBHandler):
    """
    This handler manages the SOTA log. The SOTA log entries dblog.models.SotaLog
    have a foreign key relationship with sota.models.Retry. The first argument
    passed to a log method must be a Retry object.
    """
    def create_logentry(self, model, record):
        return model(level=record.levelname, message=self.format(record), retry=record.args[0])
