# coding: utf-8
# Django settings for ninan project.
from .base import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG

MYSQL_DB = 'app_ninan'
MYSQL_USER = 'root'
MYSQL_PASS = ''
MYSQL_HOST_M = 'localhost'
MYSQL_HOST_S = 'localhost'
MYSQL_PORT = '3306'

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

ALLOWED_HOSTS = ['*']

CACHES = CACHE_USED_BY_DEBUG

# ------------------ Cache Time ---------------------------------------
NOTE_VIEW_CACHE_TIME = 1
WEIXIN_CACHE_TIME = 1

# STATICFILES_STORAGE = 'utils.storage.CachedSaeStorage'
# STATIC_URL = "http://7u2hjo.com1.z0.glb.clouddn.com/"


LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(threadName)s:%(thread)d]'
            '[%(module)s:%(lineno)d] [%(levelname)s]- %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {'()': 'django.utils.log.RequireDebugFalse'}
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
            'filters': ['require_debug_false'],
        },
        'default':  {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename':  root('logs/all.log'),
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,
            'formatter': 'standard',
        },
        'request_handler': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': root('logs/script.log'),
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,
            'formatter': 'standard',
        },
        'scprits_handler': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': root('logs/script.log'),
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,
            'formatter': 'standard',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['default'],
            'level': 'INFO',
            'propagate': False
        },
        'django.request': {
            'handlers': ['request_handler'],
            'level': 'DEBUG',
            'propagate': False
        },
        'scripts': {
            'handlers': ['scprits_handler'],
            'level': 'DEBUG',
            'propagate': False
        },
    }
}

# Used for collectstatic
import os
os.environ['sae.storage.path'] = root('storage')
os.environ['HTTP_HOST'] = '127.0.0.1:8080'

DEFAULT_FILE_STORAGE = 'baniu.django.storage.Storage'
STORAGE_BUCKET_NAME = "ninan"
STORAGE_ACCESSKEY = ''
STORAGE_SECRETKEY = ''
STORAGE_DOMAIN = "http://"
STORAGE_ALLOWED_HOST = ""

STATIC_URL = ""

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'utils.whoosh.whoosh_cn_backend_local.WhooshEngine',
        'PATH': 'whoosh',
        'STORAGE': 'file',
    },
}
