"""
Copyright (C) 2014, Jaguar Land Rover

This program is licensed under the terms and conditions of the
Mozilla Public License, version 2.0.  The full text of the 
Mozilla Public License is at https://www.mozilla.org/MPL/2.0/

Maintainer: Rudolf Streif (rstreif@jaguarlandrover.com)
Modified by: David Thiriez (david.thiriez@p3-group.com)
"""

"""
Django settings for rvi project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project
from unipath import Path
# Load secrets from non-executable JSON
import json
# Normally you should not import ANYTHING from Django directly
# into your settings, but ImproperlyConfigured is an exception.
from django.core.exceptions import ImproperlyConfigured

# Build paths inside the project like this:
BASE_DIR = Path(__file__).absolute().ancestor(3)
MEDIA_ROOT = BASE_DIR.child('media')
WEB_DIR = BASE_DIR.child('web')
# STATIC_ROOT = WEB_DIR.child("staticroot")
CONFIG_DIR = BASE_DIR.child('config')
TEMPLATE_DIRS = [WEB_DIR.child('templates')]


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# secret keys handled in /config/settings/secrets.json
# JSON-based secrets module
with open(CONFIG_DIR.child('settings', 'secrets.json')) as f:
    secrets = json.loads(f.read())


def get_secret(setting, secrets=secrets):
    """Get the secret variable or return explicit exception."""
    try:
        return secrets[setting]
    except KeyError:
        error_msg = 'Set the {0} environment variable'.format(setting)
        raise ImproperlyConfigured(error_msg)

SECRET_KEY = get_secret('DJANGO_SECRET_KEY')
GOOGLE_API_KEY = get_secret('GOOGLE_API_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
TEMPLATE_DEBUG = False

# We allow all hosts to connect
ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = (
    # 'django_admin_bootstrapped',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'bootstrap3',
    'leaflet',
    'djgeojson',
    'rvi',
    'vehicles',
    'sota',
    'dblog',
    'tracking',
    'devices',
    'security',
    'can_fw',
    'servicehistory',
    'tokenapi',
)

# INSTALLED_APPS = ('django_cassandra_engine',) + INSTALLED_APPS

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
)

ROOT_URLCONF = 'rvi.urls'

WSGI_APPLICATION = 'rvi.wsgi.application'

AUTHENTICATION_BACKENDS = ('django.contrib.auth.backends.ModelBackend', 'tokenapi.backends.TokenBackend', )
LOGIN_URL = '/login/'

# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'rvi',
        'USER': 'rvi_user',
        'PASSWORD': 'rvi',
        'CHARSET': 'utf8',
    },
}

# Logging
# https://docs.djangoproject.com/en/1.7/topics/logging/

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            # 'filename': os.path.join(BASE_DIR, 'log/rvibackend.log'),
            'filename': BASE_DIR.child('log', 'rvibackend.log'),
            'formatter': 'verbose',
        },
        'db_general': {
            'level': 'INFO',
            'class': 'dblog.handlers.DBHandler',
            'model': 'dblog.models.GeneralLog',
            'expiry': 0,
            'formatter': 'verbose',
        },
        'db_sota': {
            'level': 'INFO',
            'class': 'dblog.handlers.SotaHandler',
            'model': 'dblog.models.SotaLog',
            'expiry': 0,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['db_general', 'file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'rvi': {
            'handlers': ['db_general', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'rvi.sota': {
            'handlers': ['db_sota', 'file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'tools': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/
STATICFILES_DIRS = (
    # os.path.join(WEB_DIR, 'static'),
    WEB_DIR.child('static'),
)
# STATIC_ROOT = os.path.join(WEB_DIR, 'staticroot')
STATIC_ROOT = WEB_DIR.child('staticroot')
STATIC_URL = '/static/'


# Email configuration
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


# Bootstrap 3 Configuration
BOOTSTRAP3 = {
    'jquery_url': '//code.jquery.com/jquery-2.1.1.min.js',
    'base_url': '//netdna.bootstrapcdn.com/bootstrap/3.2.0/',
    'css_url': None,
    'theme_url': None,
    'javascript_url': None,
    'javascript_in_head': False,
    'include_jquery': True,
}


# Server Key File
# RVI_BACKEND_KEYFILE = os.path.join(BASE_DIR, 'keys/rvi_be.private.pem')
RVI_BACKEND_KEYFILE = BASE_DIR.child("keys", "insecure_root_key_priv.pem")

# Server Signature Algorithm (default: RS256)
RVI_BACKEND_ALG_SIG = 'RS256'


# File upload base path
# You can use the relative path when running the rviserver in the foreground.
# For running as a daemon you must use an absolute path.
# MEDIA_ROOT = os.path.join(BASE_DIR, 'files')
MEDIA_ROOT = BASE_DIR.child("files")
# MEDIA_ROOT = '/absolute/path/to/files/'

MEDIA_URL = '/files/'

DEFAULT_VEHICLE_IMAGE = "car-100x50.png"

# Mapping Configuration
LEAFLET_CONFIG = {
    'TILES': 'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    'MINIMAP': True,
}
LEAFLET_ANIMATION_INTERVAL = "100"

# RVI Server Daemon Configuration
RVI_DB_PING_INTERVAL = 10
RVI_DB_CLOSE_TIMEOUT = 3600
RVI_SERVICE_EDGE_URL = 'http://127.0.0.1:8801'

# SOTA
RVI_SOTA_ENABLE = False
RVI_SOTA_CALLBACK_URL = 'http://127.0.0.1:20001'
RVI_SOTA_SERVICE_ID = '/sota'
RVI_SOTA_CHUNK_SIZE = 65536

# CAN_FW
RVI_CANFW_ENABLE = False
RVI_CANFW_CALLBACK_URL = 'http://127.0.0.1:20004'
RVI_CANFW_SERVICE_ID = '/canfw'
RVI_CANFW_NUM_PRIO = 16

# Device Management
RVI_DM_SERVICE_ID = '/dm'

# Tracking
# RVI_TRACKING_SOURCE_GPS = True
RVI_TRACKING_ENABLE = False
RVI_TRACKING_CALLBACK_URL = 'http://127.0.0.1:20002'
RVI_TRACKING_SERVICE_ID = '/logging'

RVI_TRACKING_DB_PUBLISH = False

# Remote (certificate) Services
RVI_CERTIFICATE_SERVICES_ENABLE = True
RVI_CERTIFICATE_SERVICES_CALLBACK_URL = 'http://127.0.0.1:20003'
RVI_CERTIFICATE_SERVICES_CALLBACK_ID = RVI_DM_SERVICE_ID

# Service invoked logging Service
RVI_LOG_INVOKED_SERVICES_ENABLE = True
RVI_LOG_INVOKED_SERVICES_CALLBACK_URL = 'http://127.0.0.1:20004'
RVI_LOG_INVOKED_SERVICES_CALLBACK_ID = RVI_TRACKING_SERVICE_ID

# Service invoked logging Service
RVI_INVOKE_SERVICES_ENABLE = True
RVI_INVOKE_SERVICES_CALLBACK_URL = 'http://127.0.0.1:20005'
RVI_INVOKE_SERVICES_CALLBACK_ID = '/invoke'

# Publish to Kafka Message Queue
RVI_TRACKING_MQ_PUBLISH = True
RVI_TRACKING_MQ_URL = "master:6667"
RVI_TRACKING_MQ_TOPIC = "rvi"

# Read from Kafka save to HBase table
RVI_TRACKING_MQ_HBASE = False
RVI_TRACKING_MQ_HBASE_URL = "master"
RVI_TRACKING_MQ_HBASE_PORT = "9090"
RVI_TRACKING_MQ_HBASE_TABLE = "rvi"

# Login Token config
TOKEN_CHECK_ACTIVE_USER = True
