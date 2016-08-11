# coding: utf-8
# Django settings for ninan project.
import os

from .base import *

import sae.const

DEBUG = False
TEMPLATE_DEBUG = DEBUG

MYSQL_DB = sae.const.MYSQL_DB
MYSQL_USER = sae.const.MYSQL_USER
MYSQL_PASS = sae.const.MYSQL_PASS
MYSQL_HOST_M = sae.const.MYSQL_HOST
MYSQL_HOST_S = sae.const.MYSQL_HOST_S
MYSQL_PORT = sae.const.MYSQL_PORT

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': MYSQL_DB,
        'USER': MYSQL_USER,
        'PASSWORD': MYSQL_PASS,
        'HOST': MYSQL_HOST_M,
        'PORT': MYSQL_PORT,
        'TEST_CHARSET': 'utf8',
    }
}

CACHES = CACHE_USED_BY_SAE

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}

#STATICFILES_STORAGE = 'utils.storage.CachedSaeStorage'

DEFAULT_FILE_STORAGE = 'baniu.django.storage.Storage'
STORAGE_BUCKET_NAME = "ninan"
STORAGE_ACCESSKEY = ''
STORAGE_SECRETKEY = ''
STORAGE_DOMAIN = "http://"
STORAGE_ALLOWED_HOST = ""

STATIC_URL = "http://"
