#!/usr/bin/env python
# coding: utf-8

from django.conf.urls import patterns, url
from django.views.generic.base import TemplateView
from django.views.decorators.cache import cache_page
from django.conf import settings

from .genericviews import (MilestoneUserListView,
                           MilestoneRandomView,
                           MilestoneDetailView,)

cache_time = getattr(settings, 'NOTE_VIEW_CACHE_TIME', 60 * 15)

urlpatterns = patterns(
    '',
    url(r'^$', TemplateView.as_view(template_name='milestone/index.html')),
    url(r'^user/(?P<user>([\w.@+-]+))/$',
        cache_page(cache_time)(MilestoneUserListView.as_view()),
        name='milestone.userview'),
    url(r'^random/$',
        cache_page(cache_time)(MilestoneRandomView.as_view()),),
    url(r'show/(?P<pk>\d+)/$',
        cache_page(cache_time)(MilestoneDetailView.as_view()),
        name='milestone.detailview'),
)
