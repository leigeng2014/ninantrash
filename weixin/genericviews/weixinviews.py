#!/usr/bin/env python
# coding: utf-8
#
# xiaoyu <xiaokong1937@gmai.com>
#
# 2014/02/11
#
# GenericViews for weixin app
#
from django.core.cache import cache
from django.core.mail import mail_admins
from django.db.models import Q
from django.contrib.auth.models import User
from django.conf import settings
from django.utils import timezone

from .base import BaseWeiXinView
from weixin.models import WeixinConfig, WeixinReply, WeixinUser
from utils.wechat.base import BaseClient


class WeixinView(BaseWeiXinView):

    def reply_subscribe(self):
        subject = 'New subscriber of Weixin_Ninan'
        content = 'A new user has subscribed Ninan_xiaoyu. His fake name' \
                  ' is %s .' % self.to_user
        mail_admins(subject, content)
        return self.reply_text_msg(self.subscribe_msg)

    def reply_commen_usage(self):
        return self.reply_text_msg(self.usage)

    def reply_express_usage(self):
        return self.reply_text_msg(self.express_usage)

    def reply_others(self, selection):
        ''' Reply text msg for keyword partly/entirely lookups. '''
        w = WeixinReply.objects
        replies = w.filter(trigger__icontains=selection, is_valid=True)

        if not replies:
            return self.reply_text_msg(self.error_msg)

        queryset = w.filter(Q(is_valid=True),
                            Q(match_type='entirely', trigger=selection) |
                            Q(match_type='partly',
                              content__icontains=selection,
                              trigger__icontains=selection))

        if not queryset:
            return self.reply_text_msg(self.error_msg)

        reply_msg = u''
        for obj in queryset:
            reply_msg += '%s\n' % obj.content
        return self.reply_text_msg(reply_msg)

    def _before_post(self):
        cache_key = 'weixin_config'
        cache_time = 10 * 60
        result = cache.get(cache_key)
        if result:
            self.subscribe_msg = result.get('subscribe_msg')
            self.usage = result.get('usage')
            self.express_usage = result.get('express_usage')
            return

        init_weixin_config = {
            'user': User.objects.get(pk=1),
            'is_valid': True,
            'trigger_type': 'subscribe',
            'content': 'Thank you for subscribe.'
            }

        w = WeixinConfig.objects
        obj, created = w.get_or_create(is_valid=True,
                                       trigger_type='subscribe',
                                       defaults=init_weixin_config)
        self.subscribe_msg = obj.content

        init_weixin_config.update({'trigger_type': 'express_usage',
                                   'content': 'Express usage'})

        obj, created = w.get_or_create(is_valid=True,
                                       trigger_type='express_usage',
                                       defaults=init_weixin_config)
        self.express_usage = obj.content

        init_weixin_config.update({'trigger_type': 'commen_usage',
                                   'content': 'Usage'})

        obj, created = w.get_or_create(is_valid=True,
                                       trigger_type='commen_usage',
                                       defaults=init_weixin_config)
        self.usage = obj.content

        cache.set(cache_key, {
            'subscribe_msg': self.subscribe_msg,
            'usage': self.usage,
            'express_usage': self.express_usage
        }, cache_time)

    def _update_openid(self):
        try:
            self.fakeuser = WeixinUser.objects.get(openid=self.to_user)
        except WeixinUser.DoesNotExist:
            email = getattr(settings, 'WEIXIN_EMAIL')
            password = getattr(settings, 'WEIXIN_PASSWORD')
            weixin_id = getattr(settings, 'WEIXIN_ID')
            weixinClient = BaseClient(email, password, weixin_id)
            self.client = weixinClient
            msg_item = self.client.get_latest_fakeid()
            if 'fakeid' not in msg_item:
                return
            fakeid = msg_item['fakeid']
            nickname = msg_item['nick_name']
            self.fakeuser = WeixinUser(nickname=nickname,
                                       fakeid=fakeid,
                                       openid=self.to_user)
        except Exception as e:
            print e
            return
        last_msg_time = timezone.now()
        self.fakeuser.last_msg_time = last_msg_time
        self.fakeuser.save()
