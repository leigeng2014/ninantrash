# coding: utf-8
#
# xiaoyu <xiaokong1937@gmail.com>
#
# 2014/06/08
#
from django.conf.urls import patterns, url

from .views import (TimelineListViewByUser, SimditorUploadView,
                    BackupDbTriggerView,
                    BackupDbSuccessView,
                    KVDBFileView,
                    JiebaInitView,
                    SearchIndexView,
                    OACarSearchView,
                    UpdateSearchIndexView)


urlpatterns = patterns(
    '',
    url(r'user_timeline/(?P<user>([\w.@+-]+))/$',
        TimelineListViewByUser.as_view(),
        name='backends.list_by_user'),
    url(r'upload/$',
        SimditorUploadView.as_view(),
        name='backends.simditor_upload'),
    url(r'backup/$',
        BackupDbTriggerView.as_view(),),
    url(r'backupsuccess/$',
        BackupDbSuccessView.as_view(),),
    url(r'updateindex/(?P<from>\d+)/$',
        UpdateSearchIndexView.as_view()),
    url(r'kvdb/(?P<filekey>.*)$',
        KVDBFileView.as_view()),
    url(r'jieba/$',
        JiebaInitView.as_view()),
    url(r'search/$',
        SearchIndexView.as_view()),
    url(r'car/$',
        OACarSearchView.as_view()),
)
