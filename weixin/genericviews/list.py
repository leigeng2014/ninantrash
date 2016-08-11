#!/usr/bin/env python
# coding: utf-8
#
# xiaoyu <xiaokong1937@gmai.com>
#
# 2014/02/11
#
# GenericViews for weixin app
#

from django.utils.translation import ugettext_lazy as _
from django.views.generic.dates import MonthArchiveView

from note.genericviews.list import BaseNoteListView
from weixin.models import WeixinMp


class WeixinListView(BaseNoteListView):
    ''' Show Weixin List '''
    template_name = 'weixin/weixinmp_list.html'

    def get_queryset(self):
        self.page_title = _('Weixin Article List')
        queryset = WeixinMp.objects.filter(is_valid=True)
        return queryset


class WeixinListViewByAuthor(WeixinListView):
    ''' Show weixin articls by author name '''

    def get_queryset(self):
        user = self.kwargs.get('user', '')
        self.page_title = _('Weixin articls created by'
                            ' %(author)s') % {'author': user}
        queryset = WeixinMp.objects.filter(user__username=user, is_valid=True)
        return queryset


class WeixinListViewByMonth(MonthArchiveView):
    date_field = 'date_created'
    make_object_list = True
    queryset = WeixinMp.objects.filter(is_valid=True)
    template_name = 'weixin/weixinmp_list.html'
    paginate_by = 5

    def get_dated_queryset(self, ordering=None, **lookup):
        self.queryset = super(WeixinListViewByMonth,
                              self).get_dated_queryset(ordering, **lookup)
        year = self.kwargs.get('year')
        month = self.kwargs.get('month')
        self.page_title = _('Weixin articls created in %(year)s - '
                            '%(month)s ') % {'year': year, 'month': month}
        return self.queryset

    def get_dated_items(self):
        self.date_list, self.object_list, extra_content = super(
            WeixinListViewByMonth, self).get_dated_items()
        extra_content.update({'title': self.page_title})
        return self.date_list, self.object_list, extra_content
