#!/usr/bin/env python
# coding: utf-8
#
# xiaoyu <xiaokong1937@gmail.com>
#
# 2014/05/21
#
"""
GenericViews for milestone app.

"""
import random

from django.views.generic.list import ListView
from django.views.generic.base import View
from django.views.generic.detail import DetailView
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from django.http import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse

from .models import Stone


class MilestoneUserListView(ListView):
    template_name = 'milestone/milestone_list.html'

    def get_queryset(self):
        username = self.kwargs.get('user', '')
        return self._get_queryset(username)

    def _get_queryset(self, username):
        queryset = Stone.objects.filter(user__username=username, is_valid=True)
        queryset = queryset.order_by('-date_created')
        return queryset

    def get(self, request, *args, **kwargs):
        username = kwargs.get('user', '')
        user = get_object_or_404(User, username=username)
        self.object_list = self.get_queryset()
        things_count = user.thing_set.filter(is_valid=True).count()
        stone_count = user.stone_set.filter(is_valid=True).count()
        scores = user.thing_set.filter(
            is_valid=True).aggregate(total=Sum('score'))['total']

        extra_data = {
            'things_count': things_count,
            'stone_count': stone_count,
            'scores': scores,
        }

        context_data = self.get_context_data(object_list=self.object_list,
                                             user_obj=user,
                                             extra_data=extra_data)
        return self.render_to_response(context_data)


class MilestoneRandomView(View):
    """
    Timeline for milestone app.

    """
    def get(self, request, *args, **kwargs):
        user_dict_list = Stone.objects.filter(is_valid=True).values('user')
        if not user_dict_list:
            raise Http404
        unique_users = []
        for user_dict in user_dict_list:
            if user_dict['user'] not in unique_users:
                unique_users.append(user_dict['user'])
        random_user_id = random.choice(unique_users)
        user = get_object_or_404(User, pk=random_user_id)
        username = user.username
        return HttpResponseRedirect(reverse('milestone.userview',
                                            args=[username]))


class MilestoneDetailView(DetailView):
    """
    Detail view for  milestone.
    """
    queryset = Stone.objects.filter(is_valid=True)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        things = self.object.thing_set.filter(is_valid=True)
        context = self.get_context_data(object=self.object,
                                        things=things)
        return self.render_to_response(context)
