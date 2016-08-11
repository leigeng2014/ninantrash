# coding: utf-8
#
# xiaoyu <xiaokong1937@gmail.com>
#
# 2014/02/05
#
# models for reminder app.
#

from django.db import models
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import localtime

from utils.model_utils import TimeStampedModel

remind_choices = (
    ('once', _('Remind only once')),
    ('daily', _('Remind daily.')),
    ('weekly', _('Remind weekly')),
    ('workday', _('Remind only on workdays.')),
    ('interval', _('Remind at every * minutes.')),
    ('other', _('Remind on which day of a week.'))
)

remind_method_choices = (
    ('qqmail', _('Remind by QQ mail.')),
)

week_day = [unicode(_('Sunday')), unicode(_('Monday')),
            unicode(_('Tuesday')), unicode(_('Wednesday')),
            unicode(_('Thursday')), unicode(_('Friday')),
            unicode(_('Staturday'))]

# FIXME :
# Reminder or some validator like this model, should be precented as a
# contenttype model. And can be easily distributed to other app.

# FIXME:
# SMS remind or fetion remind.


class RemindMethod(TimeStampedModel):
    name = models.CharField(_('Remind method type.'),
                            choices=remind_method_choices, max_length=32)
    extra_info = models.CharField(_('Phone number or QQ number'),
                                  max_length=32)
    code = models.CharField(_('Validate code'), max_length=32)
    user = models.ForeignKey(User)
    expire_time = models.DateTimeField(_('Expire in.'))
    generated_by = models.CharField(_('Generate by.'), max_length=32)

    def __unicode__(self):
        return '%s_%s' % (self.name, self.extra_info)

    def get_absolute_url(self):
        return reverse('reminder_method_detail', kwargs={'pk': str(self.id)})

    def get_title(self):
        return dict(remind_method_choices)[self.name]

    def get_description(self):
        return _('%(title)s Target: '
                 '%(content)s.') % {'title': self.get_title(),
                                    'content': self.extra_info}

    class Meta:
        verbose_name = _('remind-method')
        verbose_name_plural = _('remind-methods')


class Reminder(TimeStampedModel):
    user = models.ForeignKey(User)
    previous_t = models.DateTimeField(_('First remind time.'),
                                      help_text=_('First remind time.'))
    next_t = models.DateTimeField(_('Next remind time.'), null=True,
                                  blank=True)
    cycle = models.CharField(_('Remind cycle.'), max_length=32,
                             help_text=_('Input numbers. If remind type is '
                                         '`Remind on which day of a week`,'
                                         'put in 1-7 splitted by comma.'))
    remind_type = models.CharField(_('Remind type.'), max_length=32,
                                   choices=remind_choices)
    title = models.CharField(_('Reminder\'s title.'), max_length=32)
    content = models.TextField(_('What to remind.'),
                               help_text=_('Content of a reminder.'
                                           'This will be sent to your phone '
                                           'or your email.'))
    method = models.ManyToManyField(RemindMethod,
                                    verbose_name=_('remind-method'))

    def __unicode__(self):
        return self.title

    def display_date(self):
        return localtime(self.next_t)
    display_date.short_description = _('Next Remind Time')

    def get_description(self):
        if self.remind_type == 'interval':
            msg = _('Remind at every %(cycle)s '
                    'minutes.') % {'cycle': self.cycle}
        elif self.remind_type == 'other':
            ids = [int(id_)-1 for id_ in self.cycle.split(',') if id_]
            days = [week_day[idx] for idx in ids]
            day_str = ' '.join(day for day in days)
            msg = _('Remind on every %(day)s of a week.') % {'day': day_str}
        else:
            msg = dict(remind_choices)[self.remind_type] or ''

        return msg
    get_description.short_description = _('Description')

    class Meta:
        verbose_name = _('reminder')
        verbose_name_plural = _('reminders')
