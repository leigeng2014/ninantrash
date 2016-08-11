#!/usr/vin/env python
# coding: utf-8
#
# xiaoyu <xiaokong1937@gmail.com>
#
# 2014/02/06
#
# Utils for ninan project.
"""Utils for Ninan project.

This module provides two function, pingback and createRandomKey.

pingback is a function used to ping back to Baidu.

"""
import urllib2
import re
import logging

logger = logging.getLogger('scripts')

from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import mail_admins

__all__ = ['pingback', 'logger']


def pingback(note):
    """
        BaiDu pingback.
        When a note is created , pingback baidu_spider to crawl the note.
    """
    debug = getattr(settings, 'DEBUG')
    if debug:
        msg = '{0} is ping BAIDU.'.format(note.title)
        logger.debug(msg)
        return
    rpc_url = 'http://ping.baidu.com/ping/RPC2'
    xml = render_to_string('bd_pingback.xml',
                           {'title': note.title,
                            'abs_url': note.get_absolute_url()})
    header = {'Content-Type': 'text/xml'}
    req = urllib2.Request(rpc_url, xml.encode('utf-8'), header)

    try:
        resp = urllib2.urlopen(req)
    except urllib2.HTTPError,  e:
        mail_admins('Baidu Pingback Error', str(e))
    except urllib2.URLError, e:
        mail_admins('Baidu Pingback Error', str(e))
    else:
        if resp.getcode() != 200:
            return resp.getcode()
        else:
            resp = resp.read().replace('\n', '').replace('\r', '')
            pattern = r'<int>(\d+)</int>'
            code = re.findall(pattern, resp)[0]
            return int(code)
