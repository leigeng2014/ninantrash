#!/usr/bin/env python
#
# xiaoyu <xiaokong1937@gmail.com>
#
# 2014/04/21
#
"""
Admin_utils for ninan project.

"""
from django.contrib import admin


class BaseUserObjectAdmin(admin.ModelAdmin):
    """
    Filte user object by request.user.
    Add user to form instance.
    """
    def queryset(self, request):
        """ Get queryset for user or all queryset for su """
        qs = super(BaseUserObjectAdmin, self).queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user, is_valid=True)

    def save_form(self, request, form, change):
        """ Save form for request.user """
        form.instance.user = request.user
        return super(BaseUserObjectAdmin, self).save_form(request, form,
                                                          change)
