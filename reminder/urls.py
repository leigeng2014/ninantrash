# ciding: utf-8
from django.conf.urls import patterns, url

from .genericviews import CheckRemindUtilView, ReminderIndexView

urlpatterns = patterns(
    '',
    url(r'^$', ReminderIndexView.as_view()),
    url(r'^check/$', CheckRemindUtilView.as_view()),
)
