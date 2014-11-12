"""
Copyright (C) 2014, Jaguar Land Rover

This program is licensed under the terms and conditions of the
Mozilla Public License, version 2.0.  The full text of the 
Mozilla Public License is at https://www.mozilla.org/MPL/2.0/

Maintainer: Rudolf Streif (rstreif@jaguarlandrover.com) 
"""

"""
Django settings for rvi project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
#BASE_DIR = os.path.dirname(os.path.dirname(__file__))
BASE_DIR = os.path.dirname(__file__)
WEB_DIR = os.path.join(BASE_DIR, 'web')

# Templates
TEMPLATE_DIRS = [os.path.join(WEB_DIR, 'templates')]

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'y7pg3qz)6fs4vk4=)_*fn(dagsx+t!wvl=p&d3ybm(yc%((&pg'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = False

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'vehicles',
    'sota',
    'dblog',
    'tracking',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'rvi.urls'

WSGI_APPLICATION = 'rvi.wsgi.application'


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
             'level': 'DEBUG',
             'class': 'logging.StreamHandler',
             'formatter': 'simple',
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'log/rvibackend.log'),
            'formatter': 'verbose',
        },
        'db_general': {
            'level': 'DEBUG',
            'class': 'dblog.handlers.DBHandler',
            'model': 'dblog.models.GeneralLog',
            'expiry': 0,
            'formatter': 'verbose',
        },
        'db_sota': {
            'level': 'DEBUG',
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
STATIC_ROOT = os.path.join(WEB_DIR, 'staticroot')
STATIC_URL = '/static/'

# File upload base path
# You can use the relative path when running the rviserver in the foreground.
# For running as a daemon you must use an absolute path.
MEDIA_ROOT = os.path.join(BASE_DIR, 'files')
#MEDIA_ROOT = '/absolute/path/to/files/'

MEDIA_URL = '/files/'

# RVI Server Daemon Configuration
RVI_SERVICE_EDGE_URL = 'http://127.0.0.1:8801'
RVI_SOTA_ENABLE = 'True'
RVI_SOTA_CALLBACK_URL = 'http://127.0.0.1:20001'
RVI_SOTA_SERVICE_ID = '/sota'
RVI_SOTA_CHUNK_SIZE = '65536'
