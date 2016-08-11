#!/usr/bin/env python
# coding: utf-8
#
# xiaoyu <xiaokong1937@gmail.com>
#
# 2014/05/07
#
"""
APIs for feedfish app

"""
from tastypie.resources import ModelResource
from tastypie import fields

from .models import FeedFish
from ninan.api import UserResource
from utils.authentication import OAuth20Authentication
from utils.authorization import UserObjectsAuthorization


class FeedFishResource(ModelResource):
    user = fields.ForeignKey(UserResource, 'user')

    class Meta:
        queryset = FeedFish.objects.filter(is_valid=True)
        resource_name = 'feedfish'
        authentication = OAuth20Authentication()
        authorization = UserObjectsAuthorization()


class PublicFishResource(ModelResource):
    user = fields.CharField(attribute='user__username')

    class Meta:
        queryset = FeedFish.objects.filter(is_valid=True)
        resource_name = 'fish'
