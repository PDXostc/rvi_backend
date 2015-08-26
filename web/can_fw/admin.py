"""
Copyright (C) 2015, Jaguar Land Rover

This program is licensed under the terms and conditions of the
Mozilla Public License, version 2.0.  The full text of the 
Mozilla Public License is at https://www.mozilla.org/MPL/2.0/

Maintainer: Rudolf Streif (rstreif@jaguarlandrover.com) 
"""

from django.contrib import admin
from django.core.urlresolvers import reverse
from can_fw.models import Rule, PackageFW, UpdateFW, Retry
import logging

logger = logging.getLogger('rvi.sota')

class PackageAdmin(admin.ModelAdmin):
    """
    Administration view for Packages
    """
    #readonly_fields = ('key_created', 'key_updated')
    list_display = ('pac_name', 'prio0x0')

class RuleAdmin(admin.ModelAdmin):
    """
    Administration view for Rules
    """
    #readonly_fields = ('key_created', 'key_updated')
    list_display = ('rule_name', 'mask', 'filt', 'id_xform', 'data_xform', 'id_operand', 'data_operand')


"""
WORK HERE
"""

class RetryInline(admin.TabularInline):
    """
    A Retry is associated with an Update. We use this Inline to show
    all Retries of an Update on the Update's detail page.
    """
    model = Retry
    readonly_fields = ('ret_start_fw', 'ret_finish_fw', 'ret_timeout_fw', 'ret_status_fw', 'get_log')

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
        (None,                  {'fields': [('upd_vehicle_fw', 'upd_package_fw')]}),
        ('Update Information',  {'fields': [('upd_status_fw', 'upd_timeout_fw', 'upd_retries_fw')]}),
    ]
    inlines = [RetryInline]

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['upd_vehicle_fw', 'upd_package_fw', 'upd_current', 'upd_status_fw']
        else:
            return ['upd_status_fw']

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

    list_display = ('update_name', 'upd_vehicle_fw', 'upd_package_fw', 'upd_status_fw', 'retry_count', 'not_expired')
    list_filter = ['upd_status_fw']
    search_fields = ['upd_vehicle__veh_name', 'upd_package__pac_name']
    actions = [start_update, abort_update]


admin.site.register(Rule, RuleAdmin)
admin.site.register(PackageFW, PackageAdmin)
admin.site.register(UpdateFW, UpdateAdmin)

