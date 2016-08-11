#!/usr/bin/python
#coding:utf-8

from django.contrib.syndication.views import Feed
from django import template
from django.utils.translation import ugettext_lazy as _

from .models import Note


class LatestNoteFeed(Feed):
    title = _("Note Feed on Ninan")
    link = '/note/'
    description = _("Latest Note Post on Ninan")

    def items(self):
        queryset = Note.objects.filter(is_valid=True, is_private=False)
        return queryset.order_by('-date_created')[:1]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        foo_template = u'{{note|safe}}'

        t = template.Template(foo_template)
        c = template.Context({'note': item.content})
        resp = t.render(c)
        return resp

    def item_author_name(self, item):
        name = item.user.username
        return name
