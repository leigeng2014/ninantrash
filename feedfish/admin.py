#!/usr/bin/env python
# coding: utf-8
#
# xiaoyu <xiaokong1937@gmail.com>
#
# 2014/04/21
#
"""
Admins for feedfish app.

"""
from django.contrib import admin
from django import forms

from utils.admin_utils import BaseUserObjectAdmin
from .models import FeedFish


class FeedFishForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        defaults = {
            'action': 'feed',
            'fish_status': 'fine',
            'fish_amount': 10,
        }
        kwargs.setdefault('initial', {}).update(defaults)
        super(FeedFishForm, self).__init__(*args, **kwargs)

    class Meta:
        model = FeedFish
        fields = ('action', 'fish_status', 'fish_amount', 'remark',
                  'fish_photo')


class FeedFishAdmin(BaseUserObjectAdmin):
    fields = ('action', 'fish_status', 'fish_amount',
              'remark', 'fish_photo')
    list_display = (
        'date_created',
        'fish_status',
        'fish_amount',
        'action',
        'remark',
    )
    form = FeedFishForm


admin.site.register(FeedFish, FeedFishAdmin)
