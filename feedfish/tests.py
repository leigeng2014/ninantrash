"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
import json

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.test.client import Client


class FeedFishTestCase(TestCase):
    fixtures = ['test_all.json']

    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)

    def test_trigger(self):
        for i in range(3):
            url = reverse('fish_trigger', kwargs={'time': i})
            resp = self.client.get(url)
            resp = json.loads(resp.content)
            self.assertEqual(resp['code'], 0)

    def test_trigger_water(self):
        url = reverse('fish_trigger_water')
        resp = self.client.get(url)
        resp = json.loads(resp.content)
        self.assertEqual(resp['code'], 0)

    def test_checkforwater(self):
        username = 'xkong'
        url = reverse('fish_check4water', kwargs={'user': username})
        resp = json.loads(self.client.get(url).content)
        self.assertEqual(resp['code'], 0)

    def test_checkforfeed(self):
        username = 'xkong'
        result = {
            0: 1,
            1: 1,
            2: 1,
        }
        for k, v in result.iteritems():
            url = reverse('fish_check4feed', kwargs={'user': username,
                                                     'time': k})
            resp = self.client.get(url)
            resp = json.loads(resp.content)
            self.assertEqual(resp['code'], v)
