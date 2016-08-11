#!/usr/bin/env python
# coding: utf-8
#
# xiaoyu <xiaokong1937@gmai.com>
#
# 2014/02/11
#
# GenericViews for weixin app
#
import json
import hashlib
import time
import re

from django.http import HttpResponse
from django.core.cache import cache
from django.core import serializers
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.conf import settings
from django.views.generic.base import View
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_exempt

from weixin.models import WeixinMp
from utils.express import wrap_express_result
from utils.supported_kd import pop_express
from utils.mixin import XMLRepsonseMixin


class BaseWeiXinView(XMLRepsonseMixin, View):

    def __init__(self, *args, **kwargs):
        super(BaseWeiXinView, self).__init__(*args, **kwargs)

        self.token = getattr(settings, 'WEIXIN_TOKEN')

        self.shortcut = []
        self.shortcutData = []

        cache_key = 'weixin_mp'
        cache_time = getattr(settings, 'WEIXIN_CACHE_TIME', 60 * 15)

        result = cache.get(cache_key)

        if result:
            self.shortcutData = result.get('shortcutData')
        else:
            queryset = WeixinMp.objects.filter(is_valid=True)
            queryset = queryset.order_by('-date_created')[:5]
            fields = ('title', 'content', 'cover_img', 'digest', )
            if queryset.exists():
                try:
                    jsondata = serializers.serialize('json', queryset,
                                                     fields=fields)
                    jsondata = json.loads(jsondata)
                    for data in jsondata:
                        key = data.get('pk')
                        obj = data.get('fields')
                        self.shortcut.append('%s:%s' % (key, obj.get('title')))
                        self.shortcutData.append({key: obj})

                    cache.set(cache_key, {
                        'shortcut': self.shortcut,
                        'shortcutData': self.shortcutData,
                    }, cache_time)

                except Exception, e:
                    if settings.DEBUG:
                        print e
                    from_ = getattr(settings, 'EMAIL_HOST_USER')
                    send_mail('exp', str(e), from_, [''])

    def get(self, request, *args, **kwargs):
        echostr = request.GET.get('echostr')
        if self.authorized(request):
            return HttpResponse(echostr)
        raise PermissionDenied

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(BaseWeiXinView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not self.authorized(request):
            raise PermissionDenied

        self._before_post()

        jsondata = self._to_json(request.body)
        self.to_user = jsondata.get('FromUserName')
        msg = jsondata.get('Content')
        msg_type = jsondata.get('MsgType')
        event = jsondata.get('Event' or None)
        self.username = jsondata.get('ToUserName')
        if msg_type == 'text':
            self._update_openid()

        # Parse msg, send response
        self.error_msg = unicode(_('Sorry but your input [%(type)s: %(msg)s]'
                                   ' is not valid.' % {'type': msg_type,
                                                       'msg': msg}))
        # Events
        if msg_type == 'event' and event == 'subscribe':
            return self.reply_subscribe()

        # Text
        if msg_type == 'text':
            selection = msg.strip().lower()
            # Usage
            if selection == '0':
                return self.reply_commen_usage()
            # Express usage.
            elif selection == '9':
                return self.reply_express_usage()
            # Article
            # Get one to five articles by selection as article count.
            elif re.match(r'^[1-5]$', selection):
                article_count = int(selection)
                article_data = self.shortcutData[:article_count]
                xml = self.get_weixinmp(article_data)
                return self.get_xml_response(xml)
            # Express Lookup
            elif selection.startswith('kd'):
                ptn = r'^kd-[a-z]+-\d+$'
                if not re.match(ptn, selection):
                    return self.reply_text_msg(self.error_msg)

                fake, com, nu = selection.split('-')
                return self.reply_text_msg(wrap_express_result(com, nu))
            # Commen express company list
            elif selection == 'kl':
                rt = u''
                for k, v in pop_express.iteritems():
                    rt += u'%s: %s\n' % (k, v)
                return self.reply_text_msg(rt)
            # Others
            else:
                return self.reply_others(selection)

        return self.reply_text_msg(self.error_msg)

    def authorized(self, request):
        signature = str(request.GET.get('signature'))
        timestamp = str(request.GET.get('timestamp'))
        nonce = str(request.GET.get('nonce'))

        params = [signature, timestamp, nonce]

        for param in params:
            if not param:
                return False

        self_params = [self.token, timestamp, nonce]
        sig = hashlib.sha1("".join(sorted(self_params))).hexdigest()

        if sig == signature:
            return True

        return False

    def reply_text_msg(self, context):

        base = {
            'ToUserName': self.to_user,
            'FromUserName': self.username,
            'CreateTime': int(time.time()),
            'MsgType': 'text',
            'Content': context,
        }

        return self.render_to_response(base)

    # Articles
    def get_weixinmp(self, article_data):
        ''' Get latest articles , send to user. '''
        article_count = len(article_data)
        article_xml = '<xml>'

        base_xml_data = {
            'ToUserName': self.to_user,
            'FromUserName': self.username,
            'CreateTime': int(time.time()),
            'MsgType': 'news',
            'ArticleCount': article_count,
        }
        base_xml_data = self._content_to_xml(base_xml_data, wrap_tag=None)

        article_xml += base_xml_data
        article_xml += '<Articles>'

        domain = Site.objects.get_current().domain

        for article_dict in article_data:
            for key, article in article_dict.iteritems():
                pic_url = article.get('cover_img')
                pic_url = '%s%s' % (getattr(settings, 'MEDIA_URL',),
                                    pic_url)
                if not pic_url.startswith('http://'):
                    pic_url = 'http://%s%s' % (domain, pic_url)
                url = 'http://%s/weixin/show/%s/' % (domain, key)
                item_xml = {
                    'Title': article.get('title'),
                    'Description': article.get('digest'),
                    'PicUrl': pic_url,
                    'Url': url,
                }
                item_xml = self._content_to_xml(item_xml, 'item')

                article_xml += item_xml

        article_xml += '</Articles>'
        article_xml += '</xml>'
        return article_xml

    def reply_subscribe(self):
        raise NotImplementedError

    def reply_commen_usage(self):
        raise NotImplementedError

    def reply_express_usage(self):
        raise NotImplementedError

    def reply_others(self):
        raise NotImplementedError

    def _before_post(self):
        ''' Init cache before post. '''

    def _update_openid(self):
        ''' Update openid for self.to_user '''
