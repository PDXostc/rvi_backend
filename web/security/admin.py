"""
Copyright (C) 2014, Jaguar Land Rover

This program is licensed under the terms and conditions of the
Mozilla Public License, version 2.0.  The full text of the 
Mozilla Public License is at https://www.mozilla.org/MPL/2.0/

Rudolf Streif (rstreif@jaguarlandrover.com) 
"""

from django.contrib import admin
from security.models import JSONWebKey, CANFWKey


class KeyAdmin(admin.ModelAdmin):
    """
    Administration view for Vehicles.
    """
    readonly_fields = ('key_kid', 'key_created', 'key_updated')
    list_display = ('key_name', 'key_kty', 'key_kid', 'not_expired')

    fieldsets = [
        (None,                    {'fields': ['key_name']}),
        ('Key Information',       {'fields': ['key_kty', 'key_kid', 'key_created', 'key_updated']}),
        ('Key Experiration',      {'fields': ['key_valid_from', 'key_valid_to']}),
        ('Algorithm Information', {'fields': ['key_alg_sig', 'key_alg_enc']}),
        ('Key Data',              {'fields': ['key_pem']}),
    ]
    
    def key_kid(self, object):
        return object.key_kid
    key_kid.short_description = 'Key Fingerprint'

class FWKeyAdmin(admin.ModelAdmin):
    """
    Administration view for Vehicles.
    """
    readonly_fields = ('key_created', 'key_updated')
    list_display = ('key_name','symm_key', 'key_created', 'key_updated')

    fieldsets = [
        (None,                    {'fields': ['key_name']}),
        ('Key Information',       {'fields': ['symm_key', 'key_created', 'key_updated']}),
    ]
    

admin.site.register(JSONWebKey, KeyAdmin)
admin.site.register(CANFWKey, FWKeyAdmin)