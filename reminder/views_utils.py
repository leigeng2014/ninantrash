# coding:utf-8
import datetime
import json

from django.conf import settings
from django.core.mail import send_mail
from django.utils.translation import ugettext_lazy as _

from utils.mixin import _obj_hook
from .workday import workday


__all__ = ['exec_remind', 'remind_qqmail', 'update_reminder']


# Don't check between the follow period.
unCheckedTime = range(16, 22)


def exec_remind(reminder, msg=''):
    methods = reminder.method.all()
    for method in methods:
        exec_from_method(reminder, method, msg)


def exec_from_method(method, msg='remind', reminder=None):
    ret = {}
    if method.name == 'qqmail':
        rc = remind_qqmail(reminder, method, msg)
        ret[method.name] = rc
    return ret


def remind_qqmail(reminder, method, msg='', title='NinanReminder'):
    if reminder:
        title = reminder.title
        msg = unicode(_(
            '[Ninan Reminder]%(title)s : %(content)s' %
            {'title': title, 'content': reminder.content}))
    ret = {}
    mailto = ['%s@qq.com' % str(method.extra_info)]
    from_ = settings.EMAIL_HOST_USER
    send_mail(title, msg, from_, mailto)
    ret['rc'] = 200
    ret['msg'] = u'QQ mail sent.'
    jsondata = json.dumps(ret)
    ret = json.loads(jsondata, object_hook=_obj_hook)
    return ret['rc']


def update_reminder(reminder):
    ''' Update next remind time. '''
    next_remind_time = None
    today = datetime.datetime.today()
    if reminder.remind_type == 'daily':
        next_remind_time = reminder.previous_t + datetime.timedelta(hours=24)
    elif reminder.remind_type == 'weekly':
        next_remind_time = reminder.previous_t + datetime.timedelta(days=7)
    elif reminder.remind_type == 'interval':
        minutes = int(reminder.cycle)
        next_remind_time = reminder.previous_t + datetime.timedelta(
            minutes=minutes)

    # workday
    elif reminder.remind_type == 'workday':
        # update next_remind_time to next workday

        # If there is no workday in this month, find next month's first workday
        if today.day > max(workday[today.month]) or \
                (today.day == workday[today.month][-1]):
            next_remind_time = reminder.previous_t.replace(month=today.month+1)
            next_remind_time = next_remind_time.replace(
                day=min(workday[today.month+1]))
        # Else, set to next workday in this month
        else:
            next_day = min([d for d in workday[today.month] if d > today.day])
            next_remind_time = reminder.previous_t.replace(day=next_day)
    elif reminder.remind_type == 'once':
        next_remind_time = reminder.previous_t
    # Every which day(s) of a week
    elif reminder.remind_type == 'other':
        _weekdays = reminder.cycle.split(',')
        weekdays = [int(d) for d in _weekdays]
        first_day = min(weekdays)
        wkdy = today.weekday() + 1
        # If there is no remind-day this week, set it to next week's first
        # remind-day
        if wkdy >= max(weekdays):
            next_day = 7 - wkdy + first_day
        # Else set to next remind-day in this week.
        else:
            min_day = min([int(d) for d in weekdays if int(d) > wkdy])
            next_day = min_day - wkdy
        next_remind_time = reminder.previous_t + datetime.timedelta(next_day)
    # Handle next_remind_time not in `unCheckedTime`
    if next_remind_time.hour in unCheckedTime:
        next_remind_time = next_remind_time.replace(hour=unCheckedTime[-1] + 1)
    reminder.next_t = next_remind_time
    reminder.save()
