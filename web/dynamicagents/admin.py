"""
Copyright (C) 2015, Jaguar Land Rover

This program is licensed under the terms and conditions of the
Mozilla Public License, version 2.0.  The full text of the 
Mozilla Public License is at https://www.mozilla.org/MPL/2.0/

Maintainer: Rudolf Streif (rstreif@jaguarlandrover.com) 

Author: Anson Fan(afan1@jaguarlandrover.com)
"""

from django.contrib import admin
from django.core.urlresolvers import reverse
from dynamicagents.models import Agent, UpdateDA, RetryDA
import logging


logger = logging.getLogger('rvi.dynamicagents')


class RetryInline(admin.TabularInline):
    """
    A Retry is associated with an Update. We use this Inline to show
    all Retries of an Update on the Update's detail page.
    """
    model = RetryDA
    readonly_fields = ('ret_start_da', 'ret_finish_da', 'ret_timeout_da', 'ret_status_da', 'get_log')

    def has_add_permission(self, request):
        return False

    def get_log(self, obj):
        """
        Returns a link to the SOTA log table view filtered for the log
        entries that belong to this Retry object.
        """
        url = reverse('admin:dblog_sotalog_changelist')
        return "<a href='{0}?retry__id__exact={1}'>Messages</a>".format(url, obj.pk)
    get_log.short_description = "Log"


class UpdateAdmin(admin.ModelAdmin):
    """
    Administration view for Updates
    """
    fieldsets = [
        (None,                  {'fields': [('upd_vehicle_da', 'upd_package_da')]}),
        ('Update Information',  {'fields': [('upd_status_da', 'upd_expiration', 'upd_retries_da')]}),
    ]
    inlines = [RetryInline]

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['upd_vehicle_da', 'upd_package_da', 'upd_current_da', 'upd_status_da']
        else:
            return ['upd_status_da']

    def start_update(self, request, updates):
        updates_started = 0
        for update in updates:
            retry = update.start()
            if retry is not None:
                logger.info('Started update: %s', retry)
                updates_started += 1
        if (updates_started == 0 ) or (updates_started > 1):
            mbit = "%s Updates were" % updates_started
        else:
            mbit = "1 Update was"
        self.message_user(request, "%s successfully started." % mbit)
    start_update.short_description = "Start selected updates"

    def abort_update(self, request, updates):
        updates_aborted = 0
        for update in updates:
            retry = update.abort()
            if retry is not None:
                logger.info('Aborted update: %s', retry)
                updates_aborted += 1
        if (updates_aborted == 0 ) or (updates_aborted > 1):
            mbit = "%s Updates were" % updates_aborted
        else:
            mbit = "1 Update was"
        self.message_user(request, "%s successfully aborted." % mbit)
    abort_update.short_description = "Abort selected updates"

    list_display = ('update_name', 'upd_vehicle_da', 'upd_package_da', 'upd_status_da', 'retry_count', 'not_expired')
    list_filter = ['upd_status_da']
    search_fields = ['upd_vehicle__veh_name', 'upd_package__pac_name']
    actions = [start_update, abort_update]


class AgentAdmin(admin.ModelAdmin):
    """
    Administration view for Packages
    """
    list_display = ('pac_name_da', 'pac_version_da')

admin.site.register(Agent, AgentAdmin)
admin.site.register(UpdateDA, UpdateAdmin)