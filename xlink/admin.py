# coding: utf-8
#
# xiaoyu <xiaokong1937@gmail.com>
#
# 2014/11/29
#
"""
Admin for xlink app.

"""
from django.contrib import admin
from django import forms
from django.utils.translation import ugettext_lazy as _

from xlink.models import Sensor, Device, DataPoint, Command
from utils.admin_utils import BaseUserObjectAdmin
from utils.mixin import DateTimePickerMixin


class DataPointForm(forms.ModelForm):
    history_time = forms.DateTimeField(
        widget=forms.TextInput(
            attrs={'onmousedown': "pickme()", 'id': 'id_previous_t'}),
        help_text=_('Click to select time.'),
        label=_('Record time.'))

    class Meta:
        model = DataPoint
        fields = ('sensor', 'value', 'history_time')


class CommandForm(forms.ModelForm):
    exp_date = forms.DateTimeField(
        widget=forms.TextInput(
            attrs={'onmousedown': "pickme()", 'id': 'id_previous_t'}),
        help_text=_('Click to select time.'),
        label=_('expire time.'))

    class Meta:
        model = Command
        fields = ('sensor', 'cmd', 'exp_date')


class DeviceAdmin(BaseUserObjectAdmin):
    fields = ('title', 'description', 'public')
    list_display = ('user', 'title', 'description', 'public')


class SensorAdmin(BaseUserObjectAdmin):
    fields = ('device', 'tipe', 'title', 'description', 'unit')
    list_display = ('id', 'user', 'title', 'device', 'tipe',
                    'description', 'unit')

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == 'device':
            kwargs["queryset"] = Device.objects.filter(user=request.user)
        return super(SensorAdmin, self).formfield_for_foreignkey(
            db_field, request, **kwargs)


class DataPointAdmin(DateTimePickerMixin, BaseUserObjectAdmin):
    fields = ('sensor', 'value', 'history_time')
    list_display = ('user', 'sensor', 'value', 'history_time')
    form = DataPointForm

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == 'sensor':
            kwargs["queryset"] = Sensor.objects.filter(user=request.user)
        return super(DataPointAdmin, self).formfield_for_foreignkey(
            db_field, request, **kwargs)


class CommandAdmin(DateTimePickerMixin, BaseUserObjectAdmin):
    fields = ('sensor', 'cmd', 'exp_date')
    list_display = ('user', 'sensor', 'cmd', 'exp_date')
    form = CommandForm

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == 'sensor':
            kwargs["queryset"] = Sensor.objects.filter(user=request.user)
        return super(CommandAdmin, self).formfield_for_foreignkey(
            db_field, request, **kwargs)


admin.site.register(Sensor, SensorAdmin)
admin.site.register(Device, DeviceAdmin)
admin.site.register(DataPoint, DataPointAdmin)
admin.site.register(Command, CommandAdmin)
