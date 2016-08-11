# coding: utf-8
#
# xiaoyu <xiaokong1937@gmail.com>
#
"""
Admins for handschopping app.

"""
from django import forms
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from utils.admin_utils import BaseUserObjectAdmin
from handschopping.models import Subscribe


SUBSCRIBE_MAX_COUNT = 3


class SubscribeForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(SubscribeForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Subscribe
        fields = ('site', 'keywords')

    def clean(self):
        cleaned_data = super(SubscribeForm, self).clean()
        site = cleaned_data.get('site')
        try:
            record = Subscribe.objects.filter(user=self.request.user,
                                              site=site)
            record_count = record.count()
        except Exception as e:
            print e
            record_count = 0
        if record_count > SUBSCRIBE_MAX_COUNT:
            raise forms.ValidationError(
                _('You could have {} records for {} site at most.').format(SUBSCRIBE_MAX_COUNT,
                                                                           site))
        return cleaned_data


class SubscribeAdmin(BaseUserObjectAdmin):
    fields = ('site', 'keywords')
    form = SubscribeForm
    list_display = (
        'user',
        'site',
        'keywords'
    )

    def get_form(self, request, obj=None, **kwargs):

        AdminForm = super(SubscribeAdmin, self).get_form(request, obj, **kwargs)

        class AdminFormWithRequest(AdminForm):

            def __new__(cls, *args, **kwargs):
                kwargs['request'] = request
                return AdminForm(*args, **kwargs)

        return AdminFormWithRequest


admin.site.register(Subscribe, SubscribeAdmin)
