# coding: utf-8
import urllib

from django.core.urlresolvers import reverse
from django.views.generic.base import View

import requests
from sae.taskqueue import add_task

from subscribe.models import Subscribe
from utils.mixin import JSONResponseMixin


class SubscribTriggerView(JSONResponseMixin, View):

    def get(self, request, *args, **kwargs):
        for subscribe in Subscribe.objects.filter(is_valid=True):
            _kwargs = {"site": subscribe.site,
                       "id": subscribe.id,
                       "keywords": subscribe.keywords}
            url = reverse('subscribe_scan')
            add_task('subscribe_q', url, payload=_kwargs)
        return self.render_to_response({'code': 0, 'msg': 'ok'})


class SubscribeParserMixin(object):
    headers = {
        'Accept': 'text/html, application/xhtml+xml, */*',
        'Accept-Language': 'zh-CN',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko',
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    def parse_smzdm(self, keywords):
        url = "http://search.smzdm.com/?c=home&s={}".format(keywords)
        encoded_url = urllib.urlencode(url)
        resp = requests.get(encoded_url, headers=self.headers)
        print resp
        return '', ''


class SubscribeScanView(SubscribeParserMixin, JSONResponseMixin, View):

    def post(self, request, *args, **kwargs):
        site = request.POST.get('site')
        keywords = request.POST.get('keywords')
        id_ = request.POST.get('id')
        try:
            subscribe = Subscribe.objects.get(pk=int(id_))
        except Subscribe.DoesNotExist:
            return self.render_to_response({'code': -1, 'msg': 'ok'})
        if site == 'smzdm':
            hash_, content = self.parse_smzdm(keywords)
        subscribe.hash = hash_
        subscribe.content = content
        subscribe.save()
        return self.render_to_response({'code': 0, 'msg': 'ok'})
