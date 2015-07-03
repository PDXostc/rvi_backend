"""
Copyright (C) 2014, Jaguar Land Rover

This program is licensed under the terms and conditions of the
Mozilla Public License, version 2.0.  The full text of the 
Mozilla Public License is at https://www.mozilla.org/MPL/2.0/

Maintainer: Rudolf Streif (rstreif@jaguarlandrover.com) 
"""

"""
Backend daemon that connects to RVI, receives, dispatches and processes
incoming messages from vehicles.
"""

from django.conf import settings



def get_setting(name, default=None):
    try:
        value = getattr(settings, name, default)
    except AttributeError:
        rvi_logger.error('RVI Server: %s not defined. Check settings!', name)
        sys.exit(1)
    return value
        

def get_settings():
        # get settings from configuration
        # service edge url
        conf = {}
        
        conf['DB_PING_INTERVAL'] = get_setting("RVI_DB_PING_INTERVAL", 10)
        conf['DB_CLOSE_TIMEOUT'] = get_setting("RVI_DB_CLOSE_TIMEOUT", 3600)
        
        conf['SERVICE_EDGE_URL']  = get_setting("RVI_SERVICE_EDGE_URL")
        conf['MEDIA_ROOT']        = get_setting("MEDIA_ROOT", ".")

        conf['SOTA_ENABLE']       = get_setting("RVI_SOTA_ENABLE", True)
        conf['SOTA_CALLBACK_URL'] = get_setting("RVI_SOTA_CALLBACK_URL")
        conf['SOTA_SERVICE_ID']   = get_setting("RVI_SOTA_SERVICE_ID", "/sota")
        conf['SOTA_CHUNK_SIZE']   = get_setting("RVI_SOTA_CHUNK_SIZE", 65536)

        conf['TRACKING_ENABLE']       = get_setting("RVI_TRACKING_ENABLE", True)
        conf['TRACKING_CALLBACK_URL'] = get_setting("RVI_TRACKING_CALLBACK_URL")
        conf['TRACKING_SERVICE_ID']   = get_setting("RVI_TRACKING_SERVICE_ID", "/logging")

        conf['TRACKING_DB_PUBLISH']   = get_setting("RVI_TRACKING_DB_PUBLISH", False)

        conf['TRACKING_MQ_PUBLISH']   = get_setting("RVI_TRACKING_MQ_PUBLISH", False)
        conf['TRACKING_MQ_URL']       = get_setting("RVI_TRACKING_MQ_URL", "localhost:9092")
        conf['TRACKING_MQ_TOPIC']     = get_setting("RVI_TRACKING_MQ_TOPIC", "rvi")
        conf['TRACKING_MQ_REPORT_FLAT']     = get_setting("RVI_TRACKING_MQ_REPORT_FLAT", False)
        
        conf['TRACKING_MQ_HBASE']     = get_setting("RVI_TRACKING_MQ_HBASE", False)
        conf['TRACKING_MQ_HBASE_URL'] = get_setting("RVI_TRACKING_MQ_HBASE_URL", "localhost")
        conf['TRACKING_MQ_HBASE_PORT'] = get_setting("RVI_TRACKING_MQ_HBASE_PORT", "9090")
        conf['TRACKING_MQ_HBASE_TABLE'] = get_setting("RVI_TRACKING_MQ_HBASE_TABLE", "rvi")

        return conf
