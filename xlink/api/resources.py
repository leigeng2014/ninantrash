# coding: utf-8
#
# xiaoyu <xiaokong1937@gmail.com>
#
# 2014/11/29
#
"""
Resources for xlink app.

"""
from tastypie import fields
from tastypie.resources import ModelResource, ALL_WITH_RELATIONS
from tastypie.authentication import ApiKeyAuthentication

from xlink.models import DataPoint, Sensor, Device, Command
from ninan.api import UserResource
from utils.authorization import UserObjectsOnlyAuthorization


class DeviceResource(ModelResource):
    user = fields.ForeignKey(UserResource, 'user')

    class Meta:
        queryset = Device.objects.filter(is_valid=True, is_private=False)
        allowed_methods = ['get', 'put', 'post', 'delete']
        authentication = ApiKeyAuthentication()
        authorization = UserObjectsOnlyAuthorization()
        fields = ['id', 'title', 'description', 'public']
        filtering = {
            'user': ALL_WITH_RELATIONS,
        }


class SensorResource(ModelResource):
    device = fields.ForeignKey(DeviceResource, 'device')
    user = fields.ForeignKey(UserResource, 'user')
    commands = fields.ToManyField('xlink.api.resources.CommandResource',
                                  'command_set',
                                  full=True)

    class Meta:
        queryset = Sensor.objects.filter(is_valid=True, is_private=False)
        allowed_methods = ['get', 'put', 'post', 'delete']
        authentication = ApiKeyAuthentication()
        authorization = UserObjectsOnlyAuthorization()
        fields = ['id', 'tipe', 'title', 'description', 'unit']
        filtering = {
            'device': ALL_WITH_RELATIONS,
            'user': ALL_WITH_RELATIONS,
            'cmd': ALL_WITH_RELATIONS
        }


class DataPointResource(ModelResource):
    sensor = fields.ForeignKey(SensorResource, 'sensor')
    user = fields.ForeignKey(UserResource, 'user')

    class Meta:
        queryset = DataPoint.objects.filter(is_valid=True, is_private=False)
        allowed_methods = ['get', 'post', 'put', 'delete']
        authentication = ApiKeyAuthentication()
        authorization = UserObjectsOnlyAuthorization()
        fields = ['id', 'date_created', 'date_modified', 'history_time',
                  'value']
        filtering = {
            'sensor': ALL_WITH_RELATIONS,
            'user': ALL_WITH_RELATIONS,
        }


class CommandResource(ModelResource):
    sensor = fields.ForeignKey(SensorResource, 'sensor')
    user = fields.ForeignKey(UserResource, 'user')

    class Meta:
        queryset = Command.objects.filter(is_valid=True)
        allowed_methods = ['get', 'post', 'put', 'delete']
        authentication = ApiKeyAuthentication()
        authorization = UserObjectsOnlyAuthorization()
        fields = ['id', 'date_created', 'exp_date',
                  'cmd']
        filtering = {
            'sensor': ALL_WITH_RELATIONS,
            'user': ALL_WITH_RELATIONS,
        }
