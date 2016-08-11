# coding: utf-8
#
# xiaokong1937@gmail.com
#

from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _

from utils.model_utils import TimeStampedModel


site_choices = (
    ('smzdm', _('smzdm')),
)


class Subscribe(TimeStampedModel):
    user = models.ForeignKey(User)
    site = models.CharField(_('site'), max_length=32, choices=site_choices)
    keywords = models.CharField(_('keywords'), max_length=256)
    latest_hash = models.CharField(_('hash'), max_length=32, blank=True, null=True)
    content = models.TextField(_('content'), blank=True, null=True)

    class Meta:
        verbose_name = _('subscribe')
        verbose_name_plural = _('subscribe')
        ordering = ['-date_created']

    def __unicode__(self):
        return "{}:{}".format(self.site, self.keywords)
