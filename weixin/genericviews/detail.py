#!/usr/bin/env python
# coding: utf-8
#
# xiaoyu <xiaokong1937@gmai.com>
#
# 2014/02/11
#
# GenericViews for weixin app
#
from django.views.generic.detail import DetailView

from weixin.models import WeixinMp


class WeixinDetailView(DetailView):
    model = WeixinMp
    # use note_detail.html as base_html template
    context_object_name = 'note'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        previous, next_ = self.get_previous_and_next()
        context = self.get_context_data(object=self.object,
                                        previous_note=previous,
                                        next_note=next_,)
        return self.render_to_response(context)

    def get_previous_and_next(self):
        '''
            Get previous and next weixin article .
        '''
        self.queryset = self.get_queryset()
        previous = self.queryset.filter(user__id=self.object.user.id,
                                        id__lt=self.object.id,
                                        is_valid=True,)
        next_ = self.queryset.filter(user__id=self.object.user.id,
                                     id__gt=self.object.id,
                                     is_valid=True,)

        previous = previous.order_by('-date_created')
        next_ = next_.order_by('date_created')
        p = previous[0] if previous else None
        n = next_[0] if next_ else None
        return (p, n)
