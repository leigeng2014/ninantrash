#!/usr/bin/env python
# coding: utf-8
#
# xiaoyu <xiaokong1937@gmail.com>
#
# 2014/04/20
#
# GenericViews for feedfish app
#
import datetime

from django.views.generic.base import View
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.utils import timezone
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.conf import settings
from django.shortcuts import get_object_or_404

from sae.taskqueue import add_task

from .models import FeedFish
from utils.mixin import JSONResponseMixin


class FeedFishIndexView(ListView):
    """ Show listed logs for feed-fish and change-water"""
    template_name = 'feedfish/index.html'
    context_object_name = 'feedfishes'
    model = FeedFish

    def get_queryset(self):
        qs = super(FeedFishIndexView, self).get_queryset()
        qs = qs.filter(is_valid=True).order_by('-date_created')[:20]
        return qs


class FeedFishShowPhotoView(DetailView):
    """
    Detail view for modal to show photo of fishes.
    """
    model = FeedFish
    template_name = 'feedfish/modal_snippet.html'


class CheckTriggerView(JSONResponseMixin, View):
    """
    This is a trigger function.
    Trigger task queue for every user to check for feed.
    """

    def get(self, request, *args, **kwargs):
        """
        Called from crontab.
        """
        # time_called : which time in a day this function is called.
        # Must in [0, 1, 2], i.e, three times a day
        time_called = kwargs.setdefault('time', 0)
        for user in User.objects.all():
            if not has_fish(user):
                continue
            _kwargs = {'time': time_called, 'user': user.username}
            url = reverse('fish_check4feed', kwargs=_kwargs)
            fish_taskq = getattr(settings, 'FEEDFISH_TASKQUEUE', 'fish')
            add_task(fish_taskq, url)
        return self.render_to_response({'code': 0, 'msg': 'ok'})


class WaterCheckTriggerView(JSONResponseMixin, View):
    """
    Trigger task queue for every user to check changing water.
    """
    def get(self, request, *args, **kwargs):
        for user in User.objects.all():
            if not has_fish(user):
                continue
            _kwargs = {'user': user.username}
            url = reverse('fish_check4water', kwargs=_kwargs)
            fish_taskq = getattr(settings, 'FEEDFISH_TASKQUEUE', 'fish')
            add_task(fish_taskq, url)
        return self.render_to_response({'code': 0, 'msg': 'ok'})


class CheckForWater(JSONResponseMixin, View):
    """
    Check if should change water for fishes.
    """
    def get(self, request, *args, **kwargs):
        username = kwargs.setdefault('user', 'xiaoyu')
        user = get_object_or_404(User, username=username)
        base_qs = FeedFish.objects.filter(user=user, is_valid=True,
                                          action='change_water')
        start_time = timezone.now() - datetime.timedelta(days=3)
        end_time = timezone.now()
        qs = base_qs.filter(date_created__range=(start_time, end_time))
        if not qs:
            remind_to_water(user)
            return self.render_to_response({'code': 1, 'msg': 'Reminded.'})
        return self.render_to_response({'code': 0, 'msg': 'ok'})


class CheckForFeed(JSONResponseMixin, View):
    """
    Check if forgot feeding fishes. If forgot, remind to feed .
    """

    def get(self, request, *args, **kwargs):
        """
        Check if we missed to feed fishes.
        Note we only check in the nearest 5 or 7 hours if we had fed the
        fishes.

        Should be called from taskqueque.
        """
        # time_called : which time in a day this function is called.
        # Must in [0, 1, 2]
        time_called = int(kwargs.setdefault('time', 0))
        username = kwargs.setdefault('user', 'xiaoyu')
        interval_config = {
            0: 12,
            1: 5,
            2: 7
        }
        user = get_object_or_404(User, username=username)
        # Check if the user still has fishes. If not, set
        # fishfeeder.have_fish to False
        base_qs = FeedFish.objects.filter(user=user, is_valid=True,
                                          action='feed')
        hour_offset = interval_config.setdefault(time_called, 12)
        end = timezone.now()
        start = end - datetime.timedelta(hours=hour_offset)
        qs = base_qs.filter(date_created__range=(start, end))
        feed_count = qs.count()
        if feed_count < 1:
            remind_to_feed(user)
            return self.render_to_response({'code': 1, 'msg': 'Reminded.'})
        return self.render_to_response({'code': 0, 'msg': 'Feeded.'})


def remind_to_feed(user):
    """
    Remind user to feed fish.
    And create a record stands for forgot feeding.
    """
    msg = _("The little fishes are hungry, go and feed them !")
    _remind_user(user, msg)
    fake_feed = FeedFish(user=user, fish_amount=1, is_valid=False,
                         action='feed', fish_status='not_feed')
    fake_feed.save()


def remind_to_water(user):
    """
    Remind user to change water for fishes.
    """
    msg = _("Go and change water for fishes! ")
    return _remind_user(user, msg)


def _remind_user(user, msg):
    """
    Send msg to user.
    """
    title = unicode(_('Ninan Feed Fish'))
    payload = u'[%s]: %s' % (title, msg)
    from reminder.views_utils import exec_from_method
    for method in user.remindmethod_set.all():
            exec_from_method(method=method, msg=payload)


def has_fish(user):
    """
    Check if the user has fishes.
    Consider the user doesn't have any fish if he didn't feed them in last
    10 days.
    """
    now = timezone.now()
    ten_days_before = now - datetime.timedelta(days=5)
    queryset = FeedFish.objects.filter(
        is_valid=True,
        user=user,
        date_created__range=(ten_days_before, now))
    if not queryset:
        return False
    return True
