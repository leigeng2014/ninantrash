#!/usr/bin/env python
# coding: utf-8
#
# xiaoyu <xiaokong1937@gmail.com>
#
# 2014/06/08
#
"""
GenericView for backends.

"""
import uuid

from django.utils.translation import ugettext_lazy as _
from django.views.generic.edit import FormView
from django.views.generic.base import View, TemplateView
from django import forms
from django.http import HttpResponse
from django.core.files.storage import default_storage
from django.utils.encoding import force_str
from django.conf import settings
from django.core.mail import mail_admins

from endless_pagination.views import AjaxListView
from sae.storage import Bucket as SaeBucket

from .models import Event
from core.utils import getNickName
from utils.mixin import JSONResponseMixin
from utils.kvdb.bucket import Bucket
from utils.car import TongdaOA


class TimelineListView(AjaxListView):
    queryset = Event.objects.filter(is_valid=True).order_by('-date_created')


class TimelineListViewByUser(AjaxListView):

    def get_queryset(self):
        user = self.kwargs.get('user', '')
        nickname = getNickName(user)
        self.page_title = _("%(user)s 's timeline") % {'user': nickname}
        queryset = Event.objects.filter(user__username=user, is_valid=True)
        queryset = queryset.order_by('-date_created')
        return queryset


# Generic Views used by simditor
class ImageForm(forms.Form):
    img = forms.ImageField()


class SimditorUploadView(JSONResponseMixin, FormView):
    form_class = ImageForm
    upload_to = getattr(settings, 'SIMDITOR_UPLOAD', 'note_image/')

    def form_invalid(self, form):
        try:
            error = form.errors.values()[-1][-1]
        except Exception as e:
            print e
            error = _('Invalid file.')
        data = {
            'success': False,
            'msg': error,
            'file_path': '',
        }
        return self.render_to_response(data)

    def form_valid(self, form):
        file_ = form.cleaned_data['img']
        ext = file_.name.split('.')[-1]
        filename = '%s%s.%s' % (self.upload_to, uuid.uuid4(), ext)
        image = default_storage.save(filename, file_)
        url = default_storage.url(image)
        data = {
            'sucess': True,
            'msg': '',
            'file_path': force_str(url)
        }
        return self.render_to_response(data)


class BackupDbTriggerView(JSONResponseMixin, View):

    def get(self, request, *args, **kwargs):
        from sae.deferredjob import MySQLExport, DeferredJob
        from sae.storage import Bucket as SBucket
        import time
        import datetime

        export_bucket = 'xkongbackup'
        bucket = SBucket(export_bucket)

        now = time.strftime('%Y_%m_%d_%H_%M_%S')
        filename = 'app_ninan_%s.zip' % now

        deferred_job = DeferredJob()
        job = MySQLExport(export_bucket, filename, 'note_note',
                          'backends/backupsuccess/')
        deferred_job.add(job)

        resp = {'touch': filename}

        #  Delete all files in this bucket created a month ago
        a_month_ago = datetime.datetime.now() - datetime.timedelta(days=30)

        for object_ in bucket.list():
            last_modified = object_['last_modified']
            if last_modified:
                mtime = datetime.datetime.strptime(last_modified,
                                                   '%Y-%m-%dT%H:%M:%S.%f')
            else:
                continue

            if object_['content_type'] is not None and mtime < a_month_ago:
                bucket.delete_object(object_['name'])

        return self.render_to_response(resp)


class BackupDbSuccessView(JSONResponseMixin, View):

    def get(self, request, *args, **kwargs):

        done = {'done': '0'}
        return self.render_to_response(done)


class UpdateSearchIndexView(JSONResponseMixin, View):

    def get(self, request, *args, **kwargs):
        from django.core.management import call_command
        from_ = kwargs.get('from', 24)
        call_command('update_index', age=int(from_))

        done = {'done': '0'}
        return self.render_to_response(done)


class KVDBFileView(View):

    def get(self, request, *args, **kwargs):
        from utils.kvdb.bucket import Bucket as SBucket
        filekey = kwargs.get('filekey')
        bucket = SBucket()
        contents = bucket.get_object_contents(filekey)
        r = HttpResponse(contents)
        r['Content-Disposition'] = 'attachment; filename={}'.format(filekey)
        return r


class JiebaInitView(JSONResponseMixin, View):

    def get(self, request, *args, **kwargs):
        # Uncomment the following two lines to allow initial.
        done = {'done': '0', 'ret': '0'}
        # return self.render_to_response(done)

        bucket_name = getattr(settings, "SAE_STORAGE_BUCKET_NAME",
                              'xkong1946')
        sae_bucket = SaeBucket(bucket_name)
        kv_bucket = Bucket()
        files = ['dict.txt', 'jieba.cache']
        ret = []
        for file_ in files:
            contents = sae_bucket.get_object_contents(file_)
            kv_bucket.save(file_, contents)
            ret.append(file_)

        done = {'done': '0', 'ret': ret}
        return self.render_to_response(done)


class SearchIndexView(TemplateView):
    template_name = 'search_index.html'

    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '')
        searched = "ajaxSearch();"
        content_data = {'query': query, 'searched': searched}
        return self.render_to_response(content_data)


class OACarSearchView(JSONResponseMixin, View):

    def get(self, request, *args, **kwargs):
        done = {'done': '0', 'ret': '0'}

        self.tongda_user = u''
        pattern = ur'济南'.encode('gbk')

        tongda = TongdaOA(self.tongda_user, '')
        if tongda.search_car(pattern):
            done.update({'ret': 'found.'})
            mail_admins(u'Car found!', '....', html_message=tongda.html)

        return self.render_to_response(done)
