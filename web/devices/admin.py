"""
Copyright (C) 2014, Jaguar Land Rover

This program is licensed under the terms and conditions of the
Mozilla Public License, version 2.0.  The full text of the 
Mozilla Public License is at https://www.mozilla.org/MPL/2.0/

Maintainer: Rudolf Streif (rstreif@jaguarlandrover.com) 
"""

from django.contrib import admin, messages
from devices.models import Device, Remote
from devices.tasks import send_remote
import logging


logger = logging.getLogger('rvi')

def replace(str):
    str.replace(" ", "<br>")
    return str

class RemoteInline(admin.TabularInline):
    """
    A Remote is associated with a Device. We use this Inline to show
    all Remotes of a Device on the Device's detail page.
    """
    model = Remote
    fieldsets = [
        (None,                  {'fields': ['rem_name']}),
        ('Device Information',  {'fields': ['rem_device']}),
        ('Vehicle Information', {'fields': ['rem_vehicle']}),
        ('Validity',            {'fields': ['rem_validfrom', 'rem_validto']}),
        ('Authorizations',      {'fields': ['rem_lock', 'rem_engine', 'rem_trunk', 'rem_horn', 'rem_lights', 'rem_windows', 'rem_hazard']}),
    ]

    def has_add_permission(self, request):
        return True


class DeviceAdmin(admin.ModelAdmin):
    """
    Administration view for Devices
    """
    fieldsets = [
        (None,                   {'fields': ['dev_name']}),
        ('Owner Information',    {'fields': ['dev_owner', 'dev_mdn']}),
        ('Device Information',   {'fields': ['dev_uuid', 'dev_min', 'dev_imei', 'dev_wifimac', 'dev_btmac']}),
        ('RVI Information',      {'fields': ['dev_rvibasename']}),
        ('Security Information', {'fields': ['dev_key']}),
    ]
    list_display = ('dev_name', 'dev_owner', 'dev_mdn', 'account')
    inlines = [RemoteInline]
    
    def save_model(self, request, obj, form, change):
        obj.account = request.user
        obj.save()


class RemoteAdmin(admin.ModelAdmin):
    """
    Administration view for Remotes
    """
    fieldsets = [
        (None,                  {'fields': ['rem_name']}),
        ('Device Information',  {'fields': ['rem_device']}),
        ('Vehicle Information', {'fields': ['rem_vehicle']}),
        ('Validity',            {'fields': ['rem_validfrom', 'rem_validto']}),
        ('Authorizations',      {'fields': ['rem_lock', 'rem_engine', 'rem_trunk', 'rem_horn', 'rem_lights', 'rem_windows', 'rem_hazard']}),
    ]
    list_display = ('rem_name', 'rem_device', 'rem_vehicle', 'rem_validfrom', 'rem_validto', 'rem_lock', 'rem_engine', 'rem_trunk', 'rem_horn', 'rem_lights', 'rem_windows', 'rem_hazard')

    def send_remotes(self, request, remotes):
        remotes_sent = 0
        for remote in remotes:
            logger.info('Sending Remote: %s', remote.get_name())
            result = send_remote(remote)
            if result:
                logger.info('Sending Remote: %s - successful', remote.get_name())
                remotes_sent += 1
            else:
                logger.error('Sending Remote: %s - failed', remote.get_name())
                self.message_user(request, "Sending Remote: %s - failed." % remote.get_name(), messages.ERROR)
        if (remotes_sent == 1):
            self.message_user(request, "%s Remote was successfully sent." % remotes_sent, messages.INFO)
        elif (remotes_sent > 1):
            self.message_user(request, "%s Remotes were successfully sent." % remotes_sent, messages.INFO)
        if (len(remotes) - remotes_sent > 0):
            self.message_user(request, "Failed sending %s Remotes." % (len(remotes) - remotes_sent), messages.WARNING)
    send_remotes.short_description = "Send selected Remotes"

    actions = [send_remotes]


admin.site.register(Device, DeviceAdmin)
admin.site.register(Remote, RemoteAdmin)
