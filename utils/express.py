#!/usr/bin/env python
# coding: utf-8
#
# xiaoyu <xiaokong1937@gmai.com>
#
# 2014/02/11
#
# Express lookup for ninan app
#
import os
import json
import urllib
import urllib2

from django.conf import settings

from supported_kd import express

DEBUG = not ('SERVER_SOFTWARE' in os.environ)


class Express(object):

    HTML_API_URL = 'http://api.ickd.cn/'

    def __init__(self):

        if not DEBUG:
            self.id = getattr(settings, 'EXPRESS_ID')
            self.secret = getattr(settings, 'EXPRESS_KEY')
        else:
            self.id = '1031'
            self.secret = '514b17'

    def lookup(self, com, nu):
        if com not in express.keys():
            rt = {'errCode': 'not a valid company'}
            rt = json.dumps(rt)
            r = json.loads(rt)
            return r
        data = {
            'id': self.id,
            'secret': self.secret,
            'com': com,
            'nu': nu,
            'type': 'json',
            'encode': 'utf8',
            'ord': 'desc',
        }
        try:
            req = '%s?%s' % (self.HTML_API_URL, urllib.urlencode(data))
            #from_ = settings.EMAIL_HOST_USER
            #send_mail('test', req, from_, ['763691951@qq.com'])
            resp = urllib2.urlopen(req)
            resp = resp.read()
        except Exception, e:
            rt = {'errCode': 'error[%s]' % str(e)}
            rt = json.dumps(rt)
            r = json.loads(rt)
            return r
        else:
            resp = json.loads(resp)
            return resp


def wrap_express_result(com, nu):
    rt = u''
    e = Express()

    resp = e.lookup(com, nu)
    if resp['errCode'] == '0':
        for data in resp['data']:
            rt += u'%s\n%s\n' % (data['time'], data['context'])
    elif resp['errCode'] == 'not a valid company':
        rt += u'暂不支持您查询的快递公司：%s' % com
    else:
        rt += json.dumps(resp)

    return rt
if __name__ == '__main__':
    print wrap_express_result('shentong', '6688')
