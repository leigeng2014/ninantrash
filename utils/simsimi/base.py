#!/usr/bin/env python
# coding: utf-8
#
# xiaoyu <xiaokong1937@gmail.com>
#
# 2014/02/23
#
# Simsimi chat tools for weixin
#
import random

from django.conf import settings

import requests


class Simsimi():

    def __init__(self):
        self.chat_url = 'http://www.simsimi.com/func/reqN'
        self.api_url = 'http://api.simsimi.com/request.p'
        self.trial_url = 'http://sandbox.api.simsimi.com/request.p'
        self.key = getattr(settings, 'SIMSIMI_KEY', '')
        self.use_api = True if self.key else False
        self.trial = True
        self.cookies = {}
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11)'
        }

        if not self.use_api:
            #self.init_cookie()
            self.cookies = {
                'selected_nc': 'ch',
                'simsimi_uid': ''
            }

    def get_result(self, message):
        referer = 'http://www.simsimi.com/talk.htm?lc=ch'
        self.headers.update({'Referer': referer})
        # Changed since 2014/04/01
        if not self.use_api:
            params = {
                'lc': 'ch',
                'req': message,
                'ft': '0.0',
            }
            resp = requests.get(self.chat_url, params=params,
                                headers=self.headers, cookies=self.cookies)
        else:
            if self.trial:
                url = self.trial_url
            else:
                url = self.api_url
            params = {
                'key': self.key,
                'text': message,
                'lc': 'ch',
                'ft': random.random(),
            }
            resp = requests.get(url, params=params)
        return resp

    def chat(self, message=''):
        if not message:
            return u'唔？'
        try:
            resp = self.get_result(message)
            answer = resp.json()['sentence_resp']
            return answer
        except:
            return random.choice([u'厄姆……', u'唔', u'...'])
