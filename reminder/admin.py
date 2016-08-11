# coding: utf-8
#
# xiaoyu <xiaokong1937@gmail.com>
#
# 2014/02/05
#
# admin for reminder app.
#
import datetime
import json
import uuid

from django.core.mail import send_mail
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.contrib import admin
from django.http import (HttpResponseRedirect, HttpResponse,
                         HttpResponseNotAllowed)
from django.conf.urls import patterns, url
from django.conf import settings

from .models import Reminder, RemindMethod
from .forms import RemindMethodForm, ReminderForm
from utils.mixin import DateTimePickerMixin
from utils.admin_utils import BaseUserObjectAdmin


class ReminderAdmin(DateTimePickerMixin, BaseUserObjectAdmin):
    fields = ('title', 'content', 'remind_type',
              'cycle', 'method', 'previous_t')
    form = ReminderForm
    list_display = ('title', 'content',
                    'get_description', 'display_date',
                    'is_valid')
    order_by = ['next_t']
    list_filter = ('next_t', 'remind_type')
    search_fields = ('title', 'content')
    date_hierarchy = 'date_created'

    def save_form(self, request, form, change):
        obj = form.instance
        obj.user = request.user
        obj.next_t = obj.previous_t.replace(second=59)
        obj.is_valid = True
        obj.save()
        return super(ReminderAdmin, self).save_form(request, form, change)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == 'method':
            kwargs["queryset"] = RemindMethod.objects.filter(user=request.user,
                                                             is_valid=True)
        return super(ReminderAdmin, self).formfield_for_manytomany(db_field,
                                                                   request,
                                                                   **kwargs)

    def add_view(self, request, form_url='', extra_context=None):
        '''
        Reimplement of add_view, check if there is remind-method by current
        user. If not, redirect to remind-method add_view.
        '''

        if not self.has_add_permission(request):
            raise PermissionDenied

        methods = RemindMethod.objects.filter(user=request.user, is_valid=True)
        if not methods:
            return HttpResponseRedirect(reverse('admin:'
                                                'reminder_remindmethod_add'))
        else:
            return super(ReminderAdmin, self).add_view(request, form_url,
                                                       extra_context)


class RemindMethodAdmin(BaseUserObjectAdmin):
    fields = ('name', 'extra_info', 'code')
    list_display = ('name', 'extra_info',
                    'user', 'generated_by',
                    'is_valid', 'expire_time')
    add_form_template = 'admin/reminder/rmv_add_form.html'
    date_hierarchy = 'date_created'
    list_filter = ('is_valid',)
    search_fields = ('name',)

    def get_urls(self):
        urls = super(RemindMethodAdmin, self).get_urls()
        my_urls = patterns(
            '',
            url(r'^getcode/$', self.admin_site.admin_view(self.get_code_view))
        )  # i.e /admin/reminder/remindmethod/getcode/
        return my_urls + urls

    def save_form(self, request, form, change):
        now = timezone.now()
        form.instance.user = request.user
        form.instance.expire_time = now + datetime.timedelta(days=2046)

        # check if the user already had a remind_method.
        try:
            obj = RemindMethod.objects.get(name=form.instance.name,
                                           user=request.user,
                                           extra_info=form.instance.extra_info,
                                           is_valid=True)
        except RemindMethod.DoesNotExist:
            pass
        else:
            form.instance.expire_time = obj.expire_time
            form.instance.generated_by = obj.generated_by
            obj.delete()
            del obj
            return super(RemindMethodAdmin, self).save_form(request, form,
                                                            change)

        try:
            obj = RemindMethod.objects.get(name=form.instance.name,
                                           user=request.user,
                                           generated_by='system',
                                           extra_info=form.instance.extra_info)
        except RemindMethod.DoesNotExist:
            if change:
                form.instance.is_valid = False
            msg = _('The remind method has been commited , but not valid.')
            tag = 'WARNING'
        else:
            if now < obj.expire_time and obj.code == form.instance.code:
                form.instance.is_valid = True
                msg = _('The remind method has been commited and validated.'
                        'You can now add reminder. ')
                tag = 'INFO'
            else:
                msg = _('The validate code was not correct.')
                tag = 'WARNING'
                form.instance.code = obj.code
                form.instance.expire_time = obj.expire_time
                form.instance.generated_by = obj.generated_by
            obj.delete()
            del obj
        self.message_user(request, msg, tag)
        return super(RemindMethodAdmin, self).save_form(request, form, change)

    def get_code_view(self, request):
        '''
        View when user press "Get validate code."
        '''
        resp_ = {}
        if request.method == 'POST':
            form = RemindMethodForm(request.POST, request.FILES)
            if form.is_valid():
                self.generate_code(request)
                resp_['code'] = 0
                resp_['msg'] = unicode(_(
                    'The validate code has been sent to %(extra_info)s . '
                    'Please input code into [Validate code] area.\nIf you '
                    'didn\'t receive it, wait for 10 minutes to send again.') %
                    {'extra_info': request.POST.get('extra_info')})
                return HttpResponse(json.dumps(resp_),
                                    content_type="application/json")
            else:
                resp_['code'] = 1
                resp_['msg'] = unicode(_('The remind type and extra_info '
                                         'are not valid.'))
                return HttpResponse(json.dumps(resp_),
                                    content_type="application/json")
        permitted_methods = ['POST', ]
        return HttpResponseNotAllowed(permitted_methods)

    def generate_code(self, request):
        '''
        Generate the validate code, send it to user.
        '''
        code = uuid.uuid4().hex[:6]
        name = request.POST.get('name')
        extra_info = request.POST.get('extra_info')
        now = timezone.now()
        expire_time = now + datetime.timedelta(minutes=10)

        obj = RemindMethod.objects.filter(name=name, extra_info=extra_info,
                                          user=request.user, is_valid=True)
        if len(obj) > 0:
            return

        obj, created = RemindMethod.objects.get_or_create(
            name=name, extra_info=extra_info, user=request.user,
            generated_by='system',
            defaults={'name': name, 'extra_info': extra_info,
                      'user': request.user, 'code': code,
                      'expire_time': expire_time,
                      'generated_by': 'system'})
        if not created:
            if now > obj.expire_time:
                obj.code = code
                obj.expire_time = expire_time
                obj.save()
            else:
                return
        self.send_code(request, code)

    def send_code(self, request, code):
        ''' Send validate code to user. '''
        data = request.POST.copy()
        name = data['name']
        extra_info = data['extra_info']
        msg = unicode(_(
            "[Ninan Reminder]: Your validate code for Ninan is "
            "%(code)s . We are sorry to bother, if this is not applied "
            "by you. Just ignore it. ") % {'code': code})

        if name == 'qqmail':
            mail_to = ['%s@qq.com' % extra_info, ]
            from_ = settings.EMAIL_HOST_USER
            send_mail(u'Ninan validation', msg, from_, mail_to)
            return 200

admin.site.register(Reminder, ReminderAdmin)
admin.site.register(RemindMethod, RemindMethodAdmin)
