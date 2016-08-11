# coding: utf-8
from django.conf import settings
from django.conf.urls import patterns, url
from django.views.decorators.cache import cache_page

from .genericviews.weixinviews import WeixinView
from .genericviews.detail import WeixinDetailView
from .genericviews.list import (WeixinListView,
                                WeixinListViewByAuthor,
                                WeixinListViewByMonth)
from .genericviews.update import (WeixinMpPublishView,
                                  WeixinMpCollectView,
                                  WeixinMpUploadView,
                                  WeixinMpImageCollectView,
                                  WeixinMpImageUploadView,)

cache_time = getattr(settings, 'WEIXIN_CACHE_TIME', 60 * 42)

urlpatterns = patterns(
    '',
    url(r'^$',
        cache_page(cache_time)(WeixinView.as_view())),
    url(r'^show/(?P<pk>\d+)/$',
        cache_page(cache_time)(WeixinDetailView.as_view()),
        name='weixin.views.detail'),
    url(r'^list/$',
        cache_page(cache_time)(WeixinListView.as_view())),
    url(r'^upload/(?P<pk>\d+)/$', WeixinMpUploadView.as_view(),
        name='weixinmp.upload'),
    url(r'^image_collect/(?P<pk>\d+)/$', WeixinMpImageCollectView.as_view(),
        name='weixinmp.image_collect'),
    url(r'^image_upload/(?P<pk>\d+)/$', WeixinMpImageUploadView.as_view(),
        name='weixinmp.image_upload'),
    url(r'^collect/$', WeixinMpCollectView.as_view()),
    url(r'^publish/$', WeixinMpPublishView.as_view()),
    url(r'^author/(?P<user>([\w.@+-]+))/$',
        cache_page(cache_time)(WeixinListViewByAuthor.as_view()),
        name='weixinauthorview'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/$',
        cache_page(cache_time)(WeixinListViewByMonth.as_view(
            month_format='%m')))
)
