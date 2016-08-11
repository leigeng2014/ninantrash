# coding: utf-8
#
# xiaoyu <xiaokong1937@gmail.com>
#
# 2014/06/08
#
"""
Utils for all.

"""
from django.contrib.auth.models import User
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.decorators.cache import cache_page
from django.conf import settings


__all__ = ['getNickName', '_wrap', 'counter_cache_page']


def getNickName(username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return username
    try:
        profile = user.profile
    #  A litte buggy, should catch `DoesNotExist`, but this function is also
    #  used by the defination file of `Profile` model. (Import error).
    except:
        return username
    return profile.nickname


def _wrap(*args, **kwargs):
    """
    Wrap Widget's media
    """
    # XXX:
    # xiaoyu @ 2014/10/01 20:17
    # When using CachedStaticFilesStorage for static files caching,
    # This function acts like ` {% static 'url' %} `
    # Used for sae storage as CachedStaticFilesStorage
    return tuple(staticfiles_storage.url(path) for path in args)


def counter_cache_page(func, counter_func):
    """
    If a counter was set to the requested model, increase counter.count
    before cache page.
    """
    cache_time = getattr(settings, "NOTE_VIEW_CACHE_TIME", 15 * 60)

    def _wrap(*args, **kwargs):
        if callable(counter_func):
            counter_func(**kwargs)
        return cache_page(cache_time)(func)(*args, **kwargs)

    return _wrap
