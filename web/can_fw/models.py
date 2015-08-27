"""
Copyright (C) 2015, Jaguar Land Rover

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

NUM_PRIO = 32

def validate_upd_timeout(timeout):
    if timeout < 0: 
        raise ValidationError("Timeout must be a positive number.")

def validate_upd_retries(retries):
    if retries <= 0:
        raise ValidationError("Retries must be 1 or larger.")

class Operator:
    """
    Operator for rules
    """
    SET = "SE"
    AND = "AN"
    OR = "OR"
    XOR = "XO"
    INV = "IN"


class Status:
    """
    Status on updates
    """
    PENDING = "PE"
    STARTED = "ST"
    RUNNING = "RU"
    ABORTED = "AB"
    SUCCESS = "SU"
    FAILED = "FA"
    WAITING = "WA"
    TIMEDOUT = "TO"

class Rule(models.Model):
    """
    Rules to be added into a package
    """
    RULE_OPERATORS = (
        (Operator.SET, "SET"),
        (Operator.AND, "AND"),
        (Operator.OR, "OR"),
        (Operator.XOR, "XOR"),
        (Operator.INV, "INV"),
    )

    #Symbolic Name in fields
    rule_name = models.CharField('Rule Name', max_length=256)
    rule_description = models.TextField('Rule Description', null=True, blank=True)

    #Rule Fields
    mask = models.CharField('Mask', max_length=8)
    filt = models.CharField('Filter', max_length=8)
    id_xform = models.CharField('ID XForm Operator', max_length=2, choices=RULE_OPERATORS, default=Operator.SET)
    data_xform = models.CharField('Data XForm Operator', max_length=2, choices=RULE_OPERATORS, default=Operator.SET)
    id_operand = models.CharField('ID Operand', max_length=8)
    data_operand = models.CharField('Data Operand', max_length=16)

    # key_created = models.DateTimeField(auto_now_add=True, editable=False)
    # key_updated = models.DateTimeField(auto_now=True, editable=False)

    pass
    def get_name(self):
        """
        Returns the rule name
        """
        return self.rule_name

    def __unicode__(self):
        """
        Returns the rule name
        """
        return self.rule_name

    class Meta:
        verbose_name = "CAN Firewall Rule"
        verbose_name_plural = "CAN Firewall Rules"


class PackageFW(models.Model):
    """
    Rule Set package description
    """

    pac_name = models.CharField('Package Name', max_length=256)
    
    # prio0x0 = models.ForeignKey(Rule, verbose_name='Rule Priority 0x0', related_name='+', null=True, blank=True)
    # prio0x1 = models.ForeignKey(Rule, verbose_name='Rule Priority 0x1', related_name='+', null=True, blank=True)
    # prio0x2 = models.ForeignKey(Rule, verbose_name='Rule Priority 0x2', related_name='+', null=True, blank=True)
    # prio0x3 = models.ForeignKey(Rule, verbose_name='Rule Priority 0x3', related_name='+', null=True, blank=True)
    # prio0x4 = models.ForeignKey(Rule, verbose_name='Rule Priority 0x4', related_name='+', null=True, blank=True)
    # prio0x5 = models.ForeignKey(Rule, verbose_name='Rule Priority 0x5', related_name='+', null=True, blank=True)
    # prio0x6 = models.ForeignKey(Rule, verbose_name='Rule Priority 0x6', related_name='+', null=True, blank=True)
    # prio0x7 = models.ForeignKey(Rule, verbose_name='Rule Priority 0x7', related_name='+', null=True, blank=True)
    # prio0x8 = models.ForeignKey(Rule, verbose_name='Rule Priority 0x8', related_name='+', null=True, blank=True)
    # prio0x9 = models.ForeignKey(Rule, verbose_name='Rule Priority 0x9', related_name='+', null=True, blank=True)
    # prio0xA = models.ForeignKey(Rule, verbose_name='Rule Priority 0xA', related_name='+', null=True, blank=True)
    # prio0xB = models.ForeignKey(Rule, verbose_name='Rule Priority 0xB', related_name='+', null=True, blank=True)
    # prio0xC = models.ForeignKey(Rule, verbose_name='Rule Priority 0xC', related_name='+', null=True, blank=True)
    # prio0xD = models.ForeignKey(Rule, verbose_name='Rule Priority 0xD', related_name='+', null=True, blank=True)
    # prio0xE = models.ForeignKey(Rule, verbose_name='Rule Priority 0xE', related_name='+', null=True, blank=True)
    # prio0xF = models.ForeignKey(Rule, verbose_name='Rule Priority 0xF', related_name='+', null=True, blank=True)

    # key_created = models.DateTimeField(auto_now_add=True, editable=False)
    # key_updated = models.DateTimeField(auto_now=True, editable=False)

    
    def get_name(self):
        """
        Returns the rule name
        """
        return self.pac_name

    def __unicode__(self):
        """
        Returns the rule name
        """
        return self.pac_name

    class Meta:
        verbose_name = "CAN Firewall Package"
        verbose_name_plural = "CAN Firewall Packages"
"""
MAJOR CHANGES HERE
"""

class UpdateFW(models.Model):
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
        (Status.TIMEDOUT, "Timeout"),
    )
    upd_vehicle_fw = models.ForeignKey(Vehicle, verbose_name='Vehicle')
    upd_package_fw = models.ForeignKey(PackageFW, verbose_name='Package')
    upd_status_fw = models.CharField('Update Status',
                                  max_length=2,
                                  choices=UPDATE_STATUS,
                                  default=Status.PENDING)
    upd_timeout_fw = models.DateTimeField('Valid Until')
    upd_retries_fw = models.IntegerField('Maximum Retries', validators=[validate_upd_retries], default="0")

    class Meta:
        verbose_name = "CAN Firewall Update"
        verbose_name_plural = "CAN Firewall Updates"
    
    @property
    def upd_status_text(self):
        return dict(self.UPDATE_STATUS)[self.upd_status_fw]
    
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
                 self.upd_package_fw.get_name() +
                 "' on '" +
                 self.upd_vehicle_fw.get_name() +
                 "'"
                )

    def not_expired(self):
        """
        Returns 'True' if this Update is not expired.
        """
        return (timezone.now() <= self.upd_timeout_fw)
    not_expired.short_description = 'Not Expired'
    not_expired.admin_order_field = 'udp_timeout'
    not_expired.boolean = True

    def retry_count(self):
        """
        Returns the number of Retry objects associated with this
        Update.
        """
        return Retry.objects.filter(ret_udpate_fw=self).count()
    retry_count.short_description = "Retry Count"

    def active_retries(self):
        """
        Returns a list with all active Retry objects associated with
        the Update. A Retry is active if its status is PENDING, STARTED,
        RUNNING or WAITING.
        """
        return Retry.objects.filter(ret_udpate_fw=self,
                                    ret_status_fw=(Status.PENDING or Status.STARTED or Status.RUNNING or Status.WAITING or Status.TIMEDOUT)
                                   )

    def start(self):
        """
        Start the update (send it to the vehicle).
        Returns the Retry object that has been created to manage the
        update process.
        """
        if self.upd_status_fw in [Status.PENDING, Status.ABORTED, Status.FAILED]:
            retry = Retry(ret_udpate_fw=self,
                          ret_start_fw=timezone.now(),
                          ret_timeout_fw=self.upd_timeout_fw,
                          ret_status_fw=Status.PENDING
                         )
            retry.save()
            self.upd_status_fw = Status.STARTED
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
        if self.upd_status_fw in [Status.STARTED, Status.RUNNING, Status.WAITING]:
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
        if not self.upd_status_fw in [Status.STARTED, Status.RUNNING, Status.WAITING]:
            super(UpdateFW, self).delete()
            
    def set_status(self, status):
        """
        Set the status of this Update object.
        """
        self.upd_status_fw = status
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
        (Status.TIMEDOUT, "Timeout"),
    )
    ret_udpate_fw = models.ForeignKey(UpdateFW, verbose_name='Update')
    ret_start_fw = models.DateTimeField('Retry Started')
    ret_timeout_fw = models.DateTimeField('Retry Valid', null=True, blank=True)
    ret_finish_fw = models.DateTimeField('Retry Finished', null=True, blank=True)
    ret_status_fw = models.CharField('Retry Status',
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
        return self.ret_udpate_fw.update_name() + " " + self.ret_start_fw.strftime("%Y-%m-%d %H:%M:%S")

    def delete(self):
        """
        Deletes this Retry. Deleting is only possible if the Retry is not
        currently active.
        """
        if not self.ret_status_fw in [Status.STARTED, Status.RUNNING, Status.WAITING]:
            super(Retry, self).delete()
            
    def set_status(self, status):
        """
        Set the status of this Retry.
        """
        self.ret_status_fw = status
        if status in [Status.ABORTED, Status.SUCCESS, Status.FAILED, Status.TIMEDOUT]:
            self.ret_finish_fw = timezone.now()
        self.save()
        
    def get_timeout_epoch(self):
        """
        Returns this Retry's timeout in seconds since epoch (1970/01/01)
        """
        return (self.ret_timeout_fw.astimezone(pytz.UTC) - datetime.datetime(1970,1,1,tzinfo=pytz.UTC)).total_seconds()


"""
END CHANGES BLOCK
"""

for prio_num in range(NUM_PRIO):
    PackageFW.add_to_class('prio_%s' % str(hex(prio_num)), models.ForeignKey(Rule, verbose_name='Rule Priority '+str(hex(prio_num)), related_name='+', null=True, blank=True))