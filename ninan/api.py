#!/usr/bin/env python
# coding: utf-8
#
# xiaoyu <xiaokong1937@gmail.com>
#
# 2014/05/07
#
"""
APIs for ninan project

"""
from django.contrib.auth.models import User

from tastypie.resources import ModelResource
from utils.authentication import OAuth20Authentication
from utils.authorization import UserOnlyAuthorization
from tastypie.authorization import ReadOnlyAuthorization


class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        fields = ['id', 'username', 'first_name', 'last_name', 'last_login']
        allowed_methods = ['get']
        authentication = OAuth20Authentication()
        authorization = ReadOnlyAuthorization()


class UserInfoResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        resource_name = 'user_info'
        fields = ['id', 'username', 'first_name', 'last_name', 'last_login']
        allowed_methods = ['get']
        authentication = OAuth20Authentication()
        authorization = UserOnlyAuthorization()
