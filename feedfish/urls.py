#!/usr/bin/env python
# coding: utf-8

from django.conf.urls import patterns, url

from .genericviews import (FeedFishIndexView,
                           FeedFishShowPhotoView,
                           CheckTriggerView,
                           CheckForFeed,
                           WaterCheckTriggerView,
                           CheckForWater)

urlpatterns = patterns(
    '',
    url(r'^$', FeedFishIndexView.as_view()),
    url(r'^show_photo/(?P<pk>\d+)/$', FeedFishShowPhotoView.as_view(),
        name='fish_show_photo'),
    url(r'^basecheck/(?P<time>\d)/$', CheckTriggerView.as_view(),
        name='fish_trigger'),
    url(r'^check/(?P<time>\d)/(?P<user>([\w\s.@+-]+))/$',
        CheckForFeed.as_view(),
        name='fish_check4feed'),
    url(r'^checkwater/$', WaterCheckTriggerView.as_view(),
        name='fish_trigger_water'),
    url(r'^water/(?P<user>([\w\s.@+-]+))/$',
        CheckForWater.as_view(),
        name='fish_check4water')
)
