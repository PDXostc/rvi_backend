"""
Copyright (C) 2015, Jaguar Land Rover

This program is licensed under the terms and conditions of the
Mozilla Public License, version 2.0.  The full text of the 
Mozilla Public License is at https://www.mozilla.org/MPL/2.0/

Maintainer: Rudolf Streif (rstreif@jaguarlandrover.com)

Author: Anson Fan (afan1@jagualandrover.com) 
"""

import datetime, pytz

from django.utils import timezone
from django.db import models
from django.core.exceptions import ValidationError

from vehicles.models import Vehicle
from tasks import notify_update


# Validators
def validate_upd_timeout_da(timeout):
    if timeout < 0:
        raise ValidationError("Timeout must be a positive number.")

def validate_upd_retries_da(retries):
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
        

class Agent(models.Model):
    """
    Software package description
    """
    pac_name_da = models.CharField('Agent Name', max_length=256)
    pac_description_da = models.TextField('Agent Description', null=True, blank=True)
    pac_version_da = models.CharField('Agent Version', max_length=256)
    pac_file_da = models.FileField('Agent File')
    pac_start_cmd = models.TextField('Agent Launch Command')
    
    def get_name(self):
        """
        Returns the package name.
        """
        return self.pac_name_da
        
    def __unicode__(self):
        """
        Returns the package name.
        """
        return self.pac_name_da


class UpdateDA(models.Model):
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
    upd_vehicle_da = models.ForeignKey(Vehicle, verbose_name='Vehicle')
    upd_package_da = models.ForeignKey(Agent, verbose_name='Agent')
    upd_status_da = models.CharField('Update Status',
                                  max_length=2,
                                  choices=UPDATE_STATUS,
                                  default=Status.PENDING)
    upd_timeout_da = models.DateTimeField('Valid Until')
    upd_retries_da = models.IntegerField('Maximum Retries', validators=[validate_upd_retries_da], default="0")
    
    @property
    def upd_status_da_text(self):
        return dict(self.UPDATE_STATUS)[self.upd_status_da]
    
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
                 self.upd_package_da.get_name() +
                 "' on '" +
                 self.upd_vehicle_da.get_name() +
                 "'"
                )

    def not_expired(self):
        """
        Returns 'True' if this Update is not expired.
        """
        return (timezone.now() <= self.upd_timeout_da)
    not_expired.short_description = 'Not Expired'
    not_expired.admin_order_field = 'udp_timeout'
    not_expired.boolean = True

    def retry_count(self):
        """
        Returns the number of Retry objects associated with this
        Update.
        """
        return Retry.objects.filter(ret_update_da=self).count()
    retry_count.short_description = "Retry Count"

    def active_retries(self):
        """
        Returns a list with all active Retry objects associated with
        the Update. A Retry is active if its status is PENDING, STARTED,
        RUNNING or WAITING.
        """
        return Retry.objects.filter(ret_update_da=self,
                                    ret_status_da=(Status.PENDING or Status.STARTED or Status.RUNNING or Status.WAITING)
                                   )

    def start(self):
        """
        Start the update (send it to the vehicle).
        Returns the Retry object that has been created to manage the
        update process.
        """
        if self.upd_status_da in [Status.PENDING, Status.ABORTED, Status.FAILED]:
            retry = Retry(ret_update_da=self,
                          ret_start_da=timezone.now(),
                          ret_timeout_da=self.upd_timeout_da,
                          ret_status_da=Status.PENDING
                         )
            retry.save()
            self.upd_status_da = Status.STARTED
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
        if self.upd_status_da in [Status.STARTED, Status.RUNNING, Status.WAITING]:
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
        if not self.upd_status_da in [Status.STARTED, Status.RUNNING, Status.WAITING]:
            super(Update, self).delete()
            
    def set_status(self, status):
        """
        Set the status of this Update object.
        """
        self.upd_status_da = status
        self.save()

                                
                
class RetryDA(models.Model):
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
    ret_update_da = models.ForeignKey(UpdateDA, verbose_name='Update')
    ret_start_da = models.DateTimeField('Retry Started')
    ret_timeout_da = models.DateTimeField('Retry Valid', null=True, blank=True)
    ret_finish_da = models.DateTimeField('Retry Finished', null=True, blank=True)
    ret_status_da = models.CharField('Retry Status',
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
        return self.ret_update_da.update_name() + " " + self.ret_start_da.strftime("%Y-%m-%d %H:%M:%S")

    def delete(self):
        """
        Deletes this Retry. Deleting is only possible if the Retry is not
        currently active.
        """
        if not self.ret_status_da in [Status.STARTED, Status.RUNNING, Status.WAITING]:
            super(RetryDA, self).delete()
            
    def set_status(self, status):
        """
        Set the status of this Retry.
        """
        self.ret_status_da = status
        if status in [Status.ABORTED, Status.SUCCESS, Status.FAILED, Status.REJECTED]:
            self.ret_finish_da = timezone.now()
        self.save()
        
    def get_timeout_epoch(self):
        """
        Returns this Retry's timeout in seconds since epoch (1970/01/01)
        """
        return (self.ret_timeout_da.astimezone(pytz.UTC) - datetime.datetime(1970,1,1,tzinfo=pytz.UTC)).total_seconds()

