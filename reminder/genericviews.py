# coding: utf-8
#
# xiaoyu <xiaokong1937@gmail.com>
#
# 2014/02/05
#
# generic_views for reminder app.
#
import datetime

from django.views.generic.base import TemplateView
from django.views.generic.list import ListView
from django.utils import timezone

from .models import Reminder
from .views_utils import exec_remind, update_reminder
from utils.mixin import JSONResponseMixin


class ReminderIndexView(TemplateView):
    template_name = 'reminder/index.html'


class CheckRemindUtilView(JSONResponseMixin, ListView):
    """
        Check if there is reminder to remind.
        This view should be called every minute.
    """
    def get_queryset(self):
        start = timezone.now()
        end = start + datetime.timedelta(minutes=1)
        return Reminder.objects.filter(next_t__gte=start,
                                       next_t__lte=end,
                                       is_valid=True)

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        if (self.get_paginate_by(self.object_list) is not None
                and hasattr(self.object_list, 'exists')):
            is_empty = not self.object_list.exists()
        else:
            is_empty = len(self.object_list) == 0
        if is_empty:
            ret = {'code': 42, 'msg': 'empty'}
        else:
            for object_ in self.object_list:
                code = exec_remind(object_)
                object_.previous_t = object_.next_t
                update_reminder(object_)
            ret = {'code': code, 'msg': 'reminded.'}
        return self.render_to_response(ret)
