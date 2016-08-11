#!/usr/bin/env python
# coding: utf-8
#
# xiaoyu <xiaokong1937@gmail.com>
#
# Tests for reminder app
#
import datetime
import json
from django.test import TestCase
from django.test.client import Client
from django.utils import timezone
from django.contrib.auth.models import User

from .models import RemindMethod, Reminder
from utils.mixin import _obj_hook
from .forms import ReminderForm, RemindMethodForm
from .views_utils import (exec_remind,
                          remind_qqmail,
                          update_reminder)


class RemindMethodFormTestCase(TestCase):
    def setUp(self):
        self.data_name1 = {'name': 'qqmail', 'extra_info': '123312'}
        self.data_name2 = {'name': 'notaqqmail', 'extra_info': '123312'}

    def test_clean(self):
        kv_result = {'10001': True,
                     '1000': False,
                     '10000000000000': False,
                     'abs': False,
                     '-1': False,
                     '<not an int>': False}
        form = RemindMethodForm(self.data_name1)
        self.assertEqual(form.is_valid(), True)

        form = RemindMethodForm(self.data_name2)
        self.assertEqual(form.is_valid(), False)

        for k, v in kv_result.iteritems():
            self.data_name1.update({'extra_info': k})
            form = RemindMethodForm(self.data_name1)
            self.assertEqual(form.is_valid(), v)


class ReminderFormTestCase(TestCase):
    def setUp(self):
        interval = {'remind_type': 'interval'}
        self.post_data = {'previous_t': timezone.now(),
                          'remind_type': '',
                          'cycle': '',
                          'title': 'test_title',
                          'content': 'test_content'}
        self.post_data.update(interval)
        user = User.objects.create_user('xiaoyu_test', 'xiaoyu@test.com',
                                        'passworrrrrrrrrd')
        self.remind_method = RemindMethod.objects.create(
            id=1, name="test", extra_info="test", code="123456",
            user=user, is_valid=True, expire_time=timezone.now(),
            date_created=timezone.now())
        self.post_data.update({'method': ('1',)})

    def test_clean_interval(self):
        kv_result = {'123': True,
                     '1': False,
                     '-1': False,
                     '0': False,
                     'abs': False,
                     '1,2,3': False,
                     '4.4': False,
                     '0x0b': False}
        for k, v in kv_result.iteritems():
            self.post_data.update({'cycle': k})
            form = ReminderForm(self.post_data)
            self.assertEqual(form.is_valid(), v)

    def test_clean_other(self):
        self.post_data.update({'remind_type': 'other'})
        kv_result = {'123': False,
                     '1': True,
                     '-1': False,
                     '0': False,
                     'abs': False,
                     '1,2,3': True,
                     '4.4': False,
                     'test,test1,1,': False}
        for k, v in kv_result.iteritems():
            self.post_data.update({'cycle': k})
            form = ReminderForm(self.post_data)
            self.assertEqual(form.is_valid(), v)


class ViewsUtilTestCase(TestCase):

    fixtures = ['test_all.xml']

    def setUp(self):
        self.reminders = Reminder.objects.all()

    def test_exec_remind(self):
        for reminder in self.reminders:
            self.assertEqual(exec_remind(reminder),
                             {u'qqmail': 200})

    def test_remind_qqmail(self):
        for reminder in self.reminders:
            method = reminder.method.get(name='qqmail')
            self.assertEqual(remind_qqmail(reminder, method), 200)

    def test_update_reminder(self):
        reminder = self.reminders[0]
        reminder.previous_t = timezone.now()
        reminder.save()

        expect = {'daily': reminder.previous_t + datetime.timedelta(hours=24),
                  'weekly': reminder.previous_t + datetime.timedelta(days=7),
                  'interval': reminder.previous_t + datetime.timedelta(
                      minutes=int(reminder.cycle)),
                  'workday': reminder.previous_t.replace(day=8),
                  'once': reminder.previous_t,
                  'other': reminder.previous_t.replace(day=10)}

        for k, v in expect.iteritems():
            reminder.previous_t = timezone.now()
            reminder.remind_type = k
            reminder.save()
            update_reminder(reminder)
            self.assertEqual(reminder.next_t.strftime('%F %T'),
                             v.strftime('%F %T'))


class AdminViewsTestCase(TestCase):

    fixtures = ['test_all.json']

    def setUp(self):
        self.client = Client()
        print self.client.login(username="xkong", password="t")

    def test_get_code(self):
        url = '/sheffield/reminder/remindmethod/getcode/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        jsondata = json.loads(response.content, object_hook=_obj_hook)
        self.assertEqual(jsondata['code'], 404)

        data = {'name': 'qqmail', 'extra_info': ''}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        jsondata = json.loads(response.content)
        self.assertEqual(jsondata['code'], 0)

        data = {'extra_info': '3'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        jsondata = json.loads(response.content)
        self.assertEqual(jsondata['code'], 1)
