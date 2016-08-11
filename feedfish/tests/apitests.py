#!/usr/bin/env python
# coding: utf-8
#
# xiaoyu <xiaokong1937@mail.com>
#
# 2014/05/08
#
"""
Tests for tastypie API.

"""
from django.contrib.auth.models import User

from tastypie.test import ResourceTestCase
from provider.oauth2.models import Client, AccessToken

from feedfish.models import FeedFish


class FeedFishResourceTest(ResourceTestCase):
    fixtures = ['test_all.json']

    def setUp(self):
        super(FeedFishResourceTest, self).setUp()
        self.base_url = '/api/v1'
        self.list_url = '%s/feedfish/' % self.base_url
        self.fish_1 = FeedFish.objects.get(pk=1)
        self.base_fish_count = 14

        username = 'fakeuser'
        password = 'fakepwd'
        self.user = User.objects.create_user(username,
                                             'fake@fake.com',
                                             password)

        self.detail_url = '%s/feedfish/%s/' % (self.base_url, self.fish_1.pk)

        self.data = {
            'user': '%s/user/%s/' % (self.base_url, self.user.pk),
            'fish_status': 'fake',
            'fish_amount': 99,
        }

    def get_credentials(self, user=None):
        """
        Return dumpheader kwargs for self.api_client.
        e.g :
          return "OAuth cc93eb6b3f609172c90c335033c5ce111c3b4eb6"
          for OAuth2
        """
        if not user:
            user = self.user

        client_ = Client(user=user, name='Fake Client %s' % user.id,
                         client_type=1, url="http://localhost")
        client_.save()

        access_token = AccessToken.objects.create(user=user,
                                                  client=client_,
                                                  scope=6)
        access_token.save()
        return "OAuth %s" % access_token.token

    def test_get_list_unauthorizied(self):
        self.assertHttpUnauthorized(
            self.api_client.get(self.list_url, format='json'))

    def test_get_list_json(self):
        resp = self.api_client.get(self.list_url, format='json',
                                   authentication=self.get_credentials())
        self.assertValidJSONResponse(resp)

        self.assertEqual(len(self.deserialize(resp)['objects']), 12)
        first_obj = self.deserialize(resp)['objects'][0]
        self.assertEqual(first_obj['id'], 14)

    def test_get_list_xml(self):
        self.assertValidXMLResponse(
            self.api_client.get(self.list_url, format='xml',
                                authentication=self.get_credentials()))

    def test_post_list_unauthenticated(self):
        self.assertHttpUnauthorized(
            self.api_client.post(self.list_url, format='json', data=self.data))

    def test_post_list(self):

        self.assertEqual(FeedFish.objects.count(), self.base_fish_count)
        self.assertHttpCreated(
            self.api_client.post(self.list_url, format='json', data=self.data,
                                 authentication=self.get_credentials()))
        self.assertEqual(FeedFish.objects.count(), self.base_fish_count + 1)

    def test_put_unauthenticated(self):
        self.assertHttpUnauthorized(
            self.api_client.put(self.detail_url, format='json', data={}))

    def test_put_detail(self):
        original_data = self.deserialize(
            self.api_client.get(self.detail_url, format='json',
                                authentication=self.get_credentials()))
        su = User.objects.get(pk=1)
        new_data = original_data.copy()
        new_data['remark'] = 'Updated: fake.'
        self.assertEqual(FeedFish.objects.count(), self.base_fish_count)
        resp = self.api_client.put(self.detail_url,
                                   format='json', data=new_data,
                                   authentication=self.get_credentials(su))
        self.assertHttpAccepted(resp)
        self.assertEqual(FeedFish.objects.count(), self.base_fish_count)
        self.assertEqual(FeedFish.objects.get(pk=1).remark, 'Updated: fake.')

    def test_delete_detail_unauthenticated(self):
        self.assertHttpUnauthorized(
            self.api_client.delete(self.detail_url, format='json'))

    def test_delete_detail(self):
        self.assertEqual(FeedFish.objects.count(), self.base_fish_count)
        self.assertHttpUnauthorized(
            self.api_client.delete(self.detail_url, format='json',
                                   authentication=self.get_credentials()))
        self.assertEqual(FeedFish.objects.count(), self.base_fish_count)

    def test_uo_put_detail(self):
        """
        uo = UserOnly.

        """
        original_data = self.deserialize(
            self.api_client.get(self.detail_url, format='json',
                                authentication=self.get_credentials()))
        new_data = original_data.copy()
        new_data['remark'] = 'Updated: fake.'
        # original_data.user != request.user
        self.assertEqual(FeedFish.objects.count(), self.base_fish_count)
        resp = self.api_client.put(self.detail_url,
                                   format='json', data=new_data,
                                   authentication=self.get_credentials())
        self.assertHttpUnauthorized(resp)
