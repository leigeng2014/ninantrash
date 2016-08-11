#coding:utf-8

from django import forms
from django.utils.translation import ugettext_lazy as _

from .models import Reminder, RemindMethod


class ReminderForm(forms.ModelForm):
    previous_t = forms.DateTimeField(
        widget=forms.TextInput(attrs={
            'onmousedown': "pickme()"}),
        help_text=_('Click to select time.'),
        label=_('First remind time.'))

    class Meta:
        model = Reminder
        fields = ('previous_t', 'remind_type', 'cycle', 'title', 'content',
                  'method')

    def clean(self):
        ''' Check if remind type and cycle is legal.'''
        cleaned_data = super(ReminderForm, self).clean()
        remind_type = cleaned_data.get('remind_type')
        cycle = cleaned_data.get('cycle')
        if remind_type == 'interval':
            try:
                test_cycle = int(cycle)
            except ValueError:
                msg = _('Remind cycle was not a valid integer.')
                self._errors['cycle'] = self.error_class([msg])
                del cleaned_data['cycle']
            else:
                if test_cycle < 10:
                    msg = _('When remind type = `every * minutes` , cycle'
                            ' should be greater than 10 minutes.')
                    self._errors['cycle'] = self.error_class([msg])
                    del cleaned_data['cycle']
                return cleaned_data
        elif remind_type == 'other':
            if cycle.find(u'，') != -1:
                cycle = cycle.replace(u'，', ',')
            for slize in cycle.split(','):
                try:
                    test_cycle = int(slize)
                except ValueError:
                    msg = _('There are invalid integers in cycle. The '
                            'integers are %(slize)s') % {'slize': slize}
                    self._errors['cycle'] = self.error_class([msg])
                    del cleaned_data['cycle']
                    return cleaned_data
                else:
                    if test_cycle not in range(1, 8):
                        msg = _('When remind type is `weekly`, cycle should '
                                'in 1~7')
                        self._errors['cycle'] = self.error_class([msg])
                        del cleaned_data['cycle']
                        return cleaned_data
            tmp_cycle = cycle.split(',')
            # Delect duplicated, resort.
            new_cycle = sorted({}.fromkeys(tmp_cycle).keys())
            rt_cycle = ','.join(v for v in new_cycle)
            cleaned_data['cycle'] = rt_cycle
            return cleaned_data
        return cleaned_data


class RemindMethodForm(forms.ModelForm):

    class Meta:
        model = RemindMethod
        fields = ('name', 'extra_info')

    def clean(self):
        ''' Clean extra_info for method. '''
        cleaned_data = super(RemindMethodForm, self).clean()
        method = cleaned_data.get('name')
        extra_info = cleaned_data.get('extra_info')
        if method == u'qqmail':
            try:
                qq = int(extra_info)
            except ValueError:
                del cleaned_data['extra_info']
                raise forms.ValidationError(_('Not a valid number.'))
            except TypeError:
                raise forms.ValidationError(_('Not a valid number.'))
            else:
                if qq <= 10000 or qq >= 999999999999:
                    del cleaned_data['extra_info']
                    raise forms.ValidationError(_('QQ not in range.'))
                else:
                    return cleaned_data
        else:
            raise forms.ValidationError(_('Not a valid method.'))
