#!/usr/bin/env python
# coding: utf-8
#
# xiaoyu <xiaokong1937@gmail.com>
#
# 2014/05/17
#
"""
Admins for milestone app.

"""
from django.contrib import admin

from .models import Stone, Thing
from utils.mixin import LimitUserMixin


class StoneAdmin(LimitUserMixin, admin.ModelAdmin):
    date_hierarchy = 'date_created'
    fields = ('title', 'description',
              'base_score',
              'achieve_score')
    list_display = ('title', 'status',
                    'current_score',
                    'achieve_score',
                    'date_created',
                    'get_thing')

    def get_thing(self, obj):
        """
        List display for stone.
        """
        return "\n".join(thing.name for thing in obj.thing_set.all())


class ThingAdmin(LimitUserMixin, admin.ModelAdmin):
    date_hierarchy = 'date_created'
    fields = ('name', 'score', 'stone')
    list_display = ('name', 'score')

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == 'stone':
            kwargs['queryset'] = Stone.objects.filter(user=request.user,
                                                      is_valid=True)
            return super(ThingAdmin, self).formfield_for_manytomany(
                db_field, request, **kwargs)

admin.site.register(Stone, StoneAdmin)
admin.site.register(Thing, ThingAdmin)
