# coding: utf-8
#
# xiaoyu <xiaokong1937@gmail.com>
#
# 2014/02/05
#
# admin for note app.
#
from django.contrib import admin
from django import forms
from django.contrib.flatpages.models import FlatPage
from django.contrib.flatpages.forms import FlatpageForm
from django.contrib.flatpages.admin import FlatPageAdmin

from .models import Profile
from utils.mixin import LimitUserMixin, SimditorMixin


class ProfileAdmin(LimitUserMixin, admin.ModelAdmin):
    model = Profile
    fields = ('nickname', 'signature', 'bio', 'avatar')
    list_display = fields


class NinanFlatpageForm(FlatpageForm):
    class Meta:
        model = FlatPage
        widgets = {
            'content': forms.Textarea(attrs={'id': 'editor'})
        }


class NinanFlatpageAdmin(SimditorMixin, FlatPageAdmin):
    form = NinanFlatpageForm


admin.site.register(Profile, ProfileAdmin)
admin.site.unregister(FlatPage)
admin.site.register(FlatPage, NinanFlatpageAdmin)
