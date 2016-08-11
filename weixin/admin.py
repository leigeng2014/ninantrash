# coding: utf-8
#
# xiaoyu <xiaokong1937@gmail.com>
#
# 2014/02/05
#
# admin for note app.
#
from django import forms
from django.contrib import admin

from .models import (WeixinMp, WeixinConfig,
                     WeixinReply, WeixinGlobalConfig,
                     WeixinUser)
from utils.mixin import LimitUserMixin, SimditorMixin


class WeixinMpForm(forms.ModelForm):
    class Meta:
        model = WeixinMp
        widgets = {
            'content': forms.Textarea(attrs={'id': 'editor'})
        }


class WeixinMpAdmin(LimitUserMixin, SimditorMixin, admin.ModelAdmin):
    date_hierarchy = 'date_created'
    fields = ('title', 'content', 'digest', 'cover_img', 'sync')
    form = WeixinMpForm
    list_display = ('title', 'user',
                    'fileid', 'show_cover_pic',
                    'sync', 'is_valid',
                    'is_published',
                    'display_created_date',)

    list_filter = ('is_published', 'date_created',)
    search_fields = ['title', 'content']


class WeixinConfigAdmin(LimitUserMixin, admin.ModelAdmin):
    date_hierarchy = 'date_created'
    fields = ('trigger_type', 'content', )
    list_display = ('trigger_type', 'content', 'date_created', 'is_valid')


class WexinReplyAdmin(WeixinConfigAdmin):
    fields = ('trigger', 'content', 'match_type')
    list_display = ('trigger', 'content',
                    'match_type', 'date_created', 'is_valid')


class WeixinGlobalConfigAdmin(admin.ModelAdmin):
    fields = ('last_article',)

    def queryset(self, request):
        qs = super(WeixinGlobalConfigAdmin, self).queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(id=99999999)


class WeixinUserAdmin(admin.ModelAdmin):
    fields = ('nickname', 'fakeid', 'openid')
    list_display = ('nickname', 'fakeid', 'openid', 'last_msg_time')

admin.site.register(WeixinMp, WeixinMpAdmin)
admin.site.register(WeixinUser, WeixinUserAdmin)
admin.site.register(WeixinReply, WexinReplyAdmin)
admin.site.register(WeixinConfig, WeixinConfigAdmin)
admin.site.register(WeixinGlobalConfig, WeixinGlobalConfigAdmin)
