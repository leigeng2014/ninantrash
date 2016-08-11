#!/usr/bin/env python
import os
import sys

DEBUG = not ('SERVER_SOFTWARE' in os.environ)
root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(root)
sys.path.insert(0, os.path.join(root, 'site-packages.zip'))
sys.path.insert(0, os.path.join(root, 'site-packages'))
os.environ['sae.kvdb.file'] = os.path.join(root, 'storage/kvdb.file')
os.environ['sae.storage.path'] = os.path.join(root, 'storage')

if DEBUG:
    os.environ['DJANGO_SETTINGS_MODULE'] = 'ninan.settings.local'
else:
    os.environ['DJANGO_SETTINGS_MODULE'] = 'ninan.settings.production'

if __name__ == "__main__":
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
