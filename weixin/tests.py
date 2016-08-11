#!/usr/bin/env python
# coding: utf-8
#
# xiaoyu <xiaokong1937@gmail.com>
#
# 2014/04/19
#
"""
Tests for app weixin.

"""
import time
import hashlib
import urllib
import random
import json

from django.test import TestCase
from django.test.client import Client
from django.conf import settings

from utils.mixin import XMLRepsonseMixin
from utils.wechat.base import BaseClient
from utils.simsimi.base import Simsimi
from .models import WeixinMp


__all__ = ['WeixinTestCase', 'WeixinPublishTestCase', 'WeChatTestCase',
           'SimsimiTestCase']


class WeixinTestCase(TestCase):
    fixtures = ['test_all.json']

    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)
        self.base_url = '/weixin/'
        self.token = settings.WEIXIN_TOKEN
        self.xml = XMLRepsonseMixin()

        self.base_msg = {
            'ToUserName': 'xiaoyu_weixin',
            'FromUserName': 'fake_username',
            'CreateTime': 1348831860,
            'MsgType': 'text',
            'Content': '',
            'Event': '',
            'MsgId': random.randint(10000000, 99999999),
        }

        now = int(time.time())
        nonce = random.randint(1000, 9999)
        params = [self.token, str(now), str(nonce)]
        sig = hashlib.sha1(''.join(sorted(params))).hexdigest()

        getdata = {
            'signature': sig,
            'timestamp': now,
            'nonce': nonce,
            'echostr': random.randint(10000, 99999)
        }

        self.base_msg.update({'CreateTime': now})

        self.url = '%s?%s' % (self.base_url, urllib.urlencode(getdata))

    def test_usage(self):
        msg = {'Content': '0'}
        self.base_msg.update(msg)
        self._sent_payload()

    def test_autherized(self):
        msg = {'Content': '0'}
        self.url = self.url.replace('signature', 'fake')
        self.base_msg.update(msg)
        payload = self.xml._content_to_xml(self.base_msg)
        resp = self.client.post(self.url, payload, content_type='text/xml')
        print resp
        self.assertEqual(resp.status_code, 403)

    def test_echostr(self):
        resp = self.client.get(self.url)
        print resp
        self.assertEqual(resp.status_code, 200)

    def test_article(self):
        msg = {'Content': str(random.randint(1, 5))}
        self.base_msg.update(msg)
        self._sent_payload()

    def test_kl(self):
        msg = {'Content': 'kl'}
        self.base_msg.update(msg)
        self._sent_payload()

    def test_kl_usage(self):
        msg = {'Content': '9'}
        self.base_msg.update(msg)
        self._sent_payload()

    def test_unicode_partly(self):
        msg = {'Content': u'匹配测试'}
        self.base_msg.update(msg)
        self._sent_payload()

    def test_others(self):
        msg = {'Content': u'你吃饭了吗？'}
        self.base_msg.update(msg)
        self._sent_payload()

    def test_unicode_entirely(self):
        msg = {'Content': u'全部匹配测试'}
        self.base_msg.update(msg)
        self._sent_payload()

    def test_kd(self):
        msg = {'Content': 'kd-sfesfes-12313213'}
        self.base_msg.update(msg)
        self._sent_payload()
        msg = {'Content': 'kd-shentong-12313213'}
        self.base_msg.update(msg)
        self._sent_payload()

        msg = {'Content': 'KD-SHENTONG-12313213'}
        self.base_msg.update(msg)
        self._sent_payload()

    def test_subscribe(self):
        msg = {'Event': 'subscribe', 'MsgType': 'event'}
        self.base_msg.update(msg)
        self._sent_payload()

    def _sent_payload(self):
        payload = self.xml._content_to_xml(self.base_msg)
        resp = self.client.post(self.url, payload, content_type='text/xml')
        print resp
        self.assertEqual(resp.status_code, 200)


class WeChatTestCase(TestCase):
    fixtures = ['test_all.json']

    def setUp(self):
        email = getattr(settings, 'WEIXIN_EMAIL')
        password = getattr(settings, 'WEIXIN_PASSWORD')
        weixin_id = getattr(settings, 'WEIXIN_ID')
        self.client = BaseClient(email, password, weixin_id)
        self.fake_user = '64500825'
        self.articles = list(WeixinMp.objects.filter(is_valid=True))[:4]

    def test_get_latest_fakeid(self):
        resp = self.client.get_latest_fakeid()
        self.assertEqual('fakeid' in resp, True)

    def test_send_msg(self):
        data = {
            'type': 1,
            'content': 'this is a test'
        }

        msg = self.client._sendMsg(self.fake_user, data)
        self.assertEqual(msg['base_resp']['err_msg'], 'ok')

    def test_send_img(self):
        img_content = open('demo.png', 'rb').read()
        file_id = self.client._uploadImg(img_content)
        data = {
            'type': 2,
            'content': '',
            'fid': file_id,
            'fileid': file_id,
        }
        msg = self.client._sendMsg(self.fake_user, data)
        self.assertEqual(msg['base_resp']['err_msg'], 'ok')

    def test_send_app_msg(self):
        self.client._addAppMsg(self.articles[:3])
        app_msg_id = self.client._getAppMsgId()
        data = {
            'type': 10,
            'fid': app_msg_id,
            'appmsgid': app_msg_id
        }

        ret_msg = self.client._sendMsg(self.fake_user, data)
        self.assertEqual(ret_msg['base_resp']['err_msg'], 'ok')

    def test_content_img_upload(self):
        img_content = open('demo.png', 'rb').read()
        msg = self.client.upload_app_content_img(img_content)
        self.assertEqual(msg['state'], 'SUCCESS')

    def test_add_app_msg(self):
        msg = self.client._addAppMsg(self.articles[-1:])
        self.assertEqual(msg['msg'], 'OK')

    def test_publish_app_msg(self):
        return
        msg_id = self.client._getAppMsgId()
        msg = self.client.publish_msg(msg_id)
        self.assertEqual(msg['base_resp']['err_msg'], 'ok')


class WeixinPublishTestCase(TestCase):
    fixtures = ['test_all.json']

    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)
        self.base_url = '/weixin/'

    def test_collect(self):
        url = '%scollect/' % self.base_url
        resp = self.client.get(url)
        resp = json.loads(resp)
        self.assertEqual(str(resp['code']), '0')

    def test_publish(self):
        url = '%spublish/' % self.base_url
        resp = self.client.get(url)
        resp = json.loads(resp)
        self.assertEqual(str(resp['code']), '0')


class SimsimiTestCase(TestCase):

    def setUp(self):
        self.backend = Simsimi()

    def test_chat(self):
        msg = random.choice([u'你好', u'你是谁', u'吃饭了吗？'])
        print self.backend.chat(msg)
