#!/usr/bin/env python
# coding: utf-8
#
# xiaoyu <xiaokong1937@gmai.com>
#
# 2014/02/11
#
"""
Generic views for weixinmp.
"""
import re
import random
from urlparse import urlparse
from urllib import urlencode

from django.views.generic.base import View
from django.views.generic.detail import BaseDetailView, SingleObjectMixin
from django.conf import settings
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from sae.taskqueue import add_task
from baniu.django.storage import Storage

from utils.mixin import JSONResponseMixin
from utils.wechat.base import BaseClient
from weixin.models import WeixinMp, WeixinGlobalConfig

__all__ = ['WeixinMpCollectView', 'WeixinMpPublishView',
           'WeixinMpUploadView', 'WeixinMpImageCollectView',
           'WeixinMpImageUploadView']


class WeixinMpCollectView(JSONResponseMixin, View):
    '''
    Collect unpublished articles, send them as one weixin article.
    '''

    def get(self, request, *args, **kwargs):
        ''' Get all unpublished weixinmps send to publish '''
        articles = WeixinMp.objects.filter(is_valid=True,
                                           is_published=False,
                                           sync=True)
        articles = articles.order_by('-date_created')[:9]
        if not articles:
            ret = {'code': 1, 'msg': '[]'}
            return self.render_to_response(ret)
        email = getattr(settings, 'WEIXIN_EMAIL')
        password = getattr(settings, 'WEIXIN_PASSWORD')
        weixin_id = getattr(settings, 'WEIXIN_ID')
        weixinClient = BaseClient(email, password, weixin_id)
        client = weixinClient
        rt = client._addAppMsg(articles)
        if rt['msg'] == 'OK':
            for article in articles:
                article.is_published = True
                article.save()
            msg_id = client._getAppMsgId()
            obj = WeixinGlobalConfig.objects.get(pk=1)
            obj.article_to_pub = int(msg_id)
            obj.save()

        ret = {'code': 0, 'msg': rt}
        return self.render_to_response(ret)


class WeixinMpPublishView(JSONResponseMixin, View):
    '''
    Publish the latest weixin article, should be called after `weixin.views
    .collect` was called.
    '''
    def get(self, request, *args, **kwargs):
        ''' GET: get all unpublish weixinmps send to publish '''
        email = getattr(settings, 'WEIXIN_EMAIL')
        password = getattr(settings, 'WEIXIN_PASSWORD')
        weixin_id = getattr(settings, 'WEIXIN_ID')
        weixinClient = BaseClient(email, password, weixin_id)
        client = weixinClient
        msg_id = client._getAppMsgId()

        obj = WeixinGlobalConfig.objects.get(pk=1)
        if obj.article_to_pub != int(msg_id):
            ret = {'code': 1, 'msg': 'No articles to publish.'}
            return self.render_to_response(ret)

        resp = client.publish_msg(msg_id)
        ret = {'code': 0, 'msg': resp}

        if resp['ret'] == '64004':  # not have masssend quota today!
            return self.render_to_response(ret)

        obj.last_article = int(msg_id)
        obj.article_to_pub = 0
        obj.save()

        return self.render_to_response(ret)


class WeixinMpUploadView(JSONResponseMixin, BaseDetailView):
    '''
    When an article was saved, call this view to upload the article's
    cover-image to Weixin server.
    Note this view should be called from task-queue to prevent multi-saved
    problem.
    '''
    model = WeixinMp

    def get(self, request, *args, **kwargs):
        ''' GET '''
        instance = self.get_object()
        if instance.cover_img == getattr(settings, 'WEIXIN_DEFAULT_COVER'):
            ret = {'code': 0, 'msg': 'Not changed.'}
            return self.render_to_response(ret)
        email = getattr(settings, 'WEIXIN_EMAIL')
        password = getattr(settings, 'WEIXIN_PASSWORD')
        weixin_id = getattr(settings, 'WEIXIN_ID')
        weixinClient = BaseClient(email, password, weixin_id)
        client = weixinClient

        bucket = Storage()
        image_content = bucket.get_object_contents(instance.cover_img.name)

        file_id = client._uploadImg(image_content)
        instance.fileid = file_id
        instance.save()

        ret = {'code': 0, 'msg': file_id}

        return self.render_to_response(ret)


class WeixinMpImageCollectView(JSONResponseMixin, BaseDetailView):
    """
    When  a weixinmp item was saved, call this view to save the images
    of the weixinmp content.
    Note this view should be called through task-queue.
    """
    model = WeixinMp

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        default_bucket = getattr(settings, 'STORAGE_BUCKET_NAME')

        content = instance.content
        pattern = r' src="(.*?)" '
        image_urls = re.findall(pattern, content)
        for url in image_urls:
            path = urlparse(url).path
            image_file_name = path.split(default_bucket)[-1]
            task_link = reverse('weixinmp.image_upload', args=(instance.pk,))
            payload = {'name': image_file_name,
                       'raw_url': url}
            payload = urlencode(payload)
            delay = random.randrange(298)
            add_task('weixin', task_link, payload=payload, delay=delay)
        return self.render_to_response({'msg': image_urls})


class WeixinMpImageUploadView(JSONResponseMixin, SingleObjectMixin, View):
    """
    Upload images in a weixinmp article.
    """

    model = WeixinMp

    def post(self, request, *args, **kwargs):
        instance = self.get_object()
        image_file_name = request.POST.get('name')
        raw_url = request.POST.get('raw_url')
        storage = Storage()
        if not image_file_name or not storage.exists(image_file_name):
            msg = 'Not a valid image.'
            code = -1
            return self.render_to_response({'msg': msg, 'code': code})
        image_file = storage.open(image_file_name)
        image_file_content = image_file.read()

        email = getattr(settings, 'WEIXIN_EMAIL')
        password = getattr(settings, 'WEIXIN_PASSWORD')
        weixin_id = getattr(settings, 'WEIXIN_ID')
        weixinClient = BaseClient(email, password, weixin_id)

        client = weixinClient
        resp = client.upload_app_content_img(image_file_content)
        url = resp['url']
        temp_content = instance.content.replace(raw_url, url)
        instance.content = temp_content
        instance.save()
        msg = 'ok'
        code = 0
        return self.render_to_response({'msg': msg, 'code': code})

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(WeixinMpImageUploadView, self).dispatch(*args, **kwargs)
