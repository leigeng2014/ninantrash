#coding:utf-8

import sae
import os
import django.core.handlers.wsgi
import sys

root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(root)

DEBUG = not ('SERVER_SOFTWARE' in os.environ)

sys.path.insert(0, os.path.join(root, 'site-packages'))
sys.path.insert(0, os.path.join(root, 'site-packages.zip'))


if DEBUG:
    os.environ['DJANGO_SETTINGS_MODULE'] = 'ninan.settings.local'
else:
    os.environ['DJANGO_SETTINGS_MODULE'] = 'ninan.settings.production'

os.environ['CERT_PATH'] = os.path.join(root, 'cacert/cacert.pem')

application=sae.create_wsgi_app(django.core.handlers.wsgi.WSGIHandler())
