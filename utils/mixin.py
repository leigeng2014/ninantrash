#!/usr/bin/env python
# coding: utf-8
#
# xiaoyu <xiaokong1937@gmai.com>
#
# 2014/02/11
#
# Mixins for ninan project
#
import xml.etree.ElementTree as ET
import json

from django.http import HttpResponse
from django.db.models import Q
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.core.exceptions import FieldError
from django.views.generic.dates import (BaseDateListView,
                                        BaseMonthArchiveView)

from endless_pagination.views import (MultipleObjectMixin,
                                      AjaxMultipleObjectTemplateResponseMixin)

from note.models import Note, TaggedItem, Category
from core.utils import _wrap

__all__ = ['PrivateObjectMixin', 'XMLRepsonseMixin', 'JSONResponseMixin',
           'LimitUserMixin', 'NoteContextMixin', 'JsonObject',
           'get_monthlist_by_queryset', '_obj_hook']


class PrivateObjectMixin(object):
    ''' Filter private object for request.user '''

    def filte_private(self, queryset):
        '''
            Filte private object for authenticated user.
        '''
        ordering = getattr(self, 'ordering', '-date_created')
        if not hasattr(self, 'request'):
            return queryset
        if not hasattr(self.request, 'user'):
            return queryset
        if self.request.user.is_authenticated():
            queryset = queryset.filter(Q(is_valid=True), Q(is_private=True) &
                                       Q(user__id=self.request.user.id) |
                                       Q(is_private=False))
        else:
            queryset = queryset.filter(is_valid=True, is_private=False)
        try:
            result = queryset.order_by(ordering)
        except FieldError:
            #  The model doesnot have an `ordering` field.
            return queryset
        return result


class XMLRepsonseMixin(object):
    """ Turn dict data into xml, response to user. """

    def render_to_response(self, context):
        return self.get_xml_response(self.convert_context_to_xml(context))

    def get_xml_response(self, content, **httpresponse_kwargs):
        return HttpResponse(content,
                            content_type='application/xml',
                            **httpresponse_kwargs)

    def convert_context_to_xml(self, context):
        return self._content_to_xml(context)

    def _add_Cdata(self, data):
        if isinstance(data, str) or isinstance(data, unicode):
            return '<![CDATA[%s]]>' % data.replace(']]>', ']]]]><![CDATA[>')
        return data

    def _content_to_xml(self, dictcontent, wrap_tag='xml'):
        xml = ''
        if wrap_tag:
            xml = '<%s>' % wrap_tag

        for k, v in dictcontent.iteritems():
            tag = k
            value = v
            xml += '<%s>%s</%s>' % (tag, self._add_Cdata(value), tag)

        if wrap_tag:
            xml += '</%s>' % wrap_tag
        return xml

    def _to_json(self, xml_body):

        json_data = {}
        root = ET.fromstring(xml_body)
        for child in root:
            if child.tag == 'CreateTime':
                value = long(child.text)
            else:
                value = child.text
            json_data[child.tag] = value

        return json_data


class JSONResponseMixin(object):
    """JSON mixin"""
    def render_to_response(self, context):
        return self.get_json_response(self.convert_context_to_json(context))

    def get_json_response(self, content, **httpresponse_kwargs):
        return HttpResponse(content,
                            content_type='application/json',
                            **httpresponse_kwargs)

    def convert_context_to_json(self, context):
        return json.dumps(context)


class LimitUserMixin(object):
    """ Mixin for admin.ModelAdmin """
    def queryset(self, request):
        qs = super(LimitUserMixin, self).queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user, is_valid=True)

    def save_form(self, request, form, change):
        """ Save form.instance.user to request.user """
        form.instance.user = request.user
        return super(LimitUserMixin, self).save_form(request, form, change)


class NoteContextMixin(object):
    def get_note_context(self):
        '''
            Return tags and note_list_by_month for view to render
        '''
        cache_key = 'common_context'
        cache_time = 86400

        result = cache.get(cache_key)

        if result:
            return result

        object_list = Note.objects.filter(is_valid=True)
        note_month_list = get_monthlist_by_queryset(object_list)

        note_type = ContentType.objects.get_for_model(Note)
        tags = TaggedItem.objects.filter(content_type__pk=note_type.id)

        tmp = []
        unique_tag_list = []
        for tag in tags:
            if tag.tag not in tmp:
                tmp.append(tag.tag)
                count = TaggedItem.objects.filter(
                    content_type__pk=note_type.id,
                    tag=tag.tag).count()
                unique_tag_list.append({'tag': tag, 'count': int(count)})

        cats = Category.objects.filter(is_valid=True)
        tmp = []
        unique_cat_list = []
        for cat in cats:
            if cat.name not in tmp:
                tmp.append(cat.name)
                category_note_count = cat.note_set.count()
                unique_cat_list.append({'cat': cat,
                                        'count': int(category_note_count)})

        AMD_ROOT = getattr(settings, "AMD_ROOT", 'sheffield')

        result = {'NOTE_TAGS': sorted(unique_tag_list,
                                      key=lambda x: x['count'],
                                      reverse=True)[:10],
                  'NOTE_MONTHLIST': note_month_list,
                  'NOTE_CATS': sorted(unique_cat_list,
                                      key=lambda x: x['count'],
                                      reverse=True),
                  'AMD_ROOT': AMD_ROOT}

        cache.set(cache_key, result, cache_time)

        return result


def _obj_hook(pairs):
    '''
    convert json object to python object.
    '''
    o = JsonObject()
    for k, v in pairs.iteritems():
        o[str(k)] = v
    return o


class JsonObject(dict):
    '''
    general json object that can bind any fields but also act as a dict.
    '''
    def __getattr__(self, attr):
        return self[attr]

    def __setattr__(self, attr, value):
        self[attr] = value

    def __getstate__(self):
        return self.copy()

    def __setstate__(self, state):
        self.update(state)


def get_monthlist_by_queryset(queryset, date_field='date_created'):
    '''
        Helper function for Note model.
        return [(year,month,note_count),...] for queryset.
    '''
    monthlist = []
    for date_ in queryset.dates(date_field, 'month'):
        year = date_.year
        month = date_.month
        count = queryset.filter(date_created__month=month,
                                date_created__year=year).count()
        if (year, month, count) not in monthlist:
            monthlist.append((year, month, int(count)))
    return monthlist


# ------------------ Used for AjaxMonthArchiveView -------------------------
class BaseAjaxDateListView(MultipleObjectMixin, BaseDateListView):
    def get(self, request, *args, **kwargs):
        self.date_list, self.object_list, extra_context = \
            self.get_dated_items()
        context = self.get_context_data(object_list=self.object_list,
                                        date_list=self.date_list,
                                        page_template=self.page_template)
        context.update(extra_context)
        return self.render_to_response(context)


class BaseAjaxMonthArchiveView(BaseMonthArchiveView, BaseAjaxDateListView):
    pass


class AjaxMonthArchiveView(AjaxMultipleObjectTemplateResponseMixin,
                           BaseAjaxMonthArchiveView):
    pass


class SimditorMixin(object):
    class Media:
        js = _wrap(*('js/simditor/module.js',
                     'js/simditor/simditor.js',
                     'js/simditor/mobilecheck.js',
                     'js/simditor/uploader.js'))
        css = {
            'all': _wrap(*('js/simditor/styles/font-awesome.css',
                           'js/simditor/styles/simditor.css'))
        }


class DateTimePickerMixin(object):
    class Media:
        css = {
            "all": _wrap(*(
                "reminder/css/jquery-ui.css",
                "reminder/css/jquery-ui-timepicker-addon.css"
            ))
        }
        js = _wrap(*(
            "reminder/js/jquery-ui.min.js",
            "reminder/js/jquery-ui-timepicker-addon.js",
            "reminder/js/jquery-ui-sliderAccess.js",
            "reminder/js/reminder.js"))
