"""
Copyright (C) 2014, Jaguar Land Rover

This program is licensed under the terms and conditions of the
Mozilla Public License, version 2.0.  The full text of the 
Mozilla Public License is at https://www.mozilla.org/MPL/2.0/

Maintainer: Rudolf Streif (rstreif@jaguarlandrover.com) 
"""

import datetime, pytz

from django.utils import timezone
from django.db import models
from django.core.exceptions import ValidationError

from vehicles.models import Vehicle
from tasks import notify_update


# Validators
def validate_upd_timeout(timeout):
    if timeout < 0:
        raise ValidationError("Timeout must be a positive number.")

def validate_upd_retries(retries):
    if retries <= 0:
        raise ValidationError("Retries must be 1 or larger.")


class Status:
    """
    Status values for Update and Retry
    """
    PENDING  = "PE"
    STARTED  = "ST"
    RUNNING  = "RU"
    ABORTED  = "AB"
    SUCCESS  = "SU"
    FAILED   = "FA"
    WAITING  = "WA"
    REJECTED = "RE"
        

class Package(models.Model):
    """
    Software package description
    """
    pac_name = models.CharField('Package Name', max_length=256)
    pac_description = models.TextField('Package Description', null=True, blank=True)
    pac_version = models.CharField('Package Version', max_length=256)
    pac_arch = models.CharField('Package Architecture', max_length=256)
    pac_file = models.FileField('Package File')
    
    def get_name(self):
        """
        Returns the package name.
        """
        return self.pac_name
        
    def __unicode__(self):
        """
        Returns the package name.
        """
        return self.pac_name


class Update(models.Model):
    """
    Update description
    An Update is defined by a vehicle and a software package that to
    be sent to that vehicle. 
    """
    UPDATE_STATUS = (
        (Status.PENDING,  "Pending"),
        (Status.STARTED,  "Started"),
        (Status.RUNNING,  "Running"),
        (Status.ABORTED,  "Aborted"),
        (Status.SUCCESS,  "Success"),
        (Status.FAILED,   "Failed"),
        (Status.WAITING,  "Waiting"),
        (Status.REJECTED, "Rejected"),
    )
    upd_vehicle = models.ForeignKey(Vehicle, verbose_name='Vehicle')
    upd_package = models.ForeignKey(Package, verbose_name='Package')
    upd_status = models.CharField('Update Status',
                                  max_length=2,
                                  choices=UPDATE_STATUS,
                                  default=Status.PENDING)
    upd_timeout = models.DateTimeField('Valid Until')
    upd_retries = models.IntegerField('Maximum Retries', validators=[validate_upd_retries], default="0")
    
    def __unicode__(self):
        """
        Returns the Update name.
        """
        return self.update_name()

    def update_name(self):
        """
        Returns the Update name composed of
        <package name> on <vehicle>.
        """
        return ("'" +
                 self.upd_package.get_name() +
                 "' on '" +
                 self.upd_vehicle.get_name() +
                 "'"
                )

    def not_expired(self):
        """
        Returns 'True' if this Update is not expired.
        """
        return (timezone.now() <= self.upd_timeout)
    not_expired.short_description = 'Not Expired'
    not_expired.admin_order_field = 'udp_timeout'
    not_expired.boolean = True

    def retry_count(self):
        """
        Returns the number of Retry objects associated with this
        Update.
        """
        return Retry.objects.filter(ret_update=self).count()
    retry_count.short_description = "Retry Count"

    def active_retries(self):
        """
        Returns a list with all active Retry objects associated with
        the Update. A Retry is active if its status is PENDING, STARTED,
        RUNNING or WAITING.
        """
        return Retry.objects.filter(ret_update=self,
                                    ret_status=(Status.PENDING or Status.STARTED or Status.RUNNING or Status.WAITING)
                                   )

    def start(self):
        """
        Start the update (send it to the vehicle).
        Returns the Retry object that has been created to manage the
        update process.
        """
        if self.upd_status in [Status.PENDING, Status.ABORTED, Status.FAILED]:
            retry = Retry(ret_update=self,
                          ret_start=timezone.now(),
                          ret_timeout=self.upd_timeout,
                          ret_status=Status.PENDING
                         )
            retry.save()
            self.upd_status = Status.STARTED
            self.save()
            notify_update(retry)
            return retry
        else:
            return None

    def abort(self):
        """
        Abort the Update and currently running Retry.
        Returns the Retry object handling the update.
        """
        if self.upd_status in [Status.STARTED, Status.RUNNING, Status.WAITING]:
            retries = self.active_retries()
            retry = None
            if retries:
                retry = retries[0]
                retry.set_status(Status.ABORTED)
            self.set_status(Status.ABORTED)
            return retry
        else:
            return None

    def delete(self):
        """
        Delete this Update object.
        Update objects can only be deleted if they are not currently
        active.
        """
        if not self.upd_status in [Status.STARTED, Status.RUNNING, Status.WAITING]:
            super(Update, self).delete()
            
    def set_status(self, status):
        """
        Set the status of this Update object.
        """
        self.upd_status = status
        self.save()

                                
                
class Retry(models.Model):
    """
    Retry objects handle the actual update. They represent the state
    of the update. Messages are logged against a Retry. That allows
    comparing update attempts in case of failures etc.
    """
    RETRY_STATUS = (
        (Status.PENDING,  "Pending"),
        (Status.STARTED,  "Started"),
        (Status.RUNNING,  "Running"),
        (Status.ABORTED,  "Aborted"),
        (Status.SUCCESS,  "Success"),
        (Status.FAILED,   "Failed"),
        (Status.WAITING,  "Waiting"),
        (Status.REJECTED, "Rejected"),
    )
    ret_update = models.ForeignKey(Update, verbose_name='Update')
    ret_start = models.DateTimeField('Retry Started')
    ret_timeout = models.DateTimeField('Retry Valid', null=True, blank=True)
    ret_finish = models.DateTimeField('Retry Finished', null=True, blank=True)
    ret_status = models.CharField('Retry Status',
                                  max_length=2,
                                  choices=RETRY_STATUS,
                                  default=Status.PENDING)
                                  
    class Meta:
        verbose_name_plural = "Retries"

    def __unicode__(self):
        """
        Returns the name of this Retry which is composed of the name
        of the Update and the start date/time of the Retry.
        """
        return self.ret_update.update_name() + " " + self.ret_start.strftime("%Y-%m-%d %H:%M:%S")

    def delete(self):
        """
        Deletes this Retry. Deleting is only possible if the Retry is not
        currently active.
        """
        if not self.ret_status in [Status.STARTED, Status.RUNNING, Status.WAITING]:
            super(Retry, self).delete()
            
    def set_status(self, status):
        """
        Set the status of this Retry.
        """
        self.ret_status = status
        if status in [Status.ABORTED, Status.SUCCESS, Status.FAILED, Status.REJECTED]:
            self.ret_finish = timezone.now()
        self.save()
        
    def get_timeout_epoch(self):
        """
        Returns this Retry's timeout in seconds since epoch (1970/01/01)
        """
        return (self.ret_timeout.astimezone(pytz.UTC) - datetime.datetime(1970,1,1,tzinfo=pytz.UTC)).total_seconds()

