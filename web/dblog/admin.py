"""
Copyright (C) 2014, Jaguar Land Rover

This program is licensed under the terms and conditions of the
Mozilla Public License, version 2.0.  The full text of the 
Mozilla Public License is at https://www.mozilla.org/MPL/2.0/

Maintainer: Rudolf Streif (rstreif@jaguarlandrover.com) 
"""

from django.contrib import admin
from dblog.models import GeneralLog, SotaLog


class LogAdmin(admin.ModelAdmin):
    """
    Administration view for logging.
    """
    list_display = ('time_seconds', 'level', 'message')
    readonly_fields = ('time', 'level', 'message')
    list_filter = ['time', 'level']
    search_fields = ['message',]

    def has_add_permission(self, request):
        return False

    def time_seconds(self, obj):
        return obj.time.strftime("%Y-%m-%d %H:%M:%S")
    time_seconds.short_description = 'Timestamp'
    
    class Meta:
        abstract = True


class GeneralLogAdmin(LogAdmin):
    """
    Aministration view for general logging.
    """
    pass


class SotaLogAdmin(LogAdmin):
    """
    Administration view for SOTA logging.
    """
    pass


# Register your models here.
admin.site.register(GeneralLog, GeneralLogAdmin)
admin.site.register(SotaLog, SotaLogAdmin)
