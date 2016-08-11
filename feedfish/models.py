# coding: utf-8
#
# xiaoyu <xiaokong1937@gmail.com>
#
# 2014/04/20
#
# models for feedfish app.
#
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.conf import settings

from utils.model_utils import TimeStampedModel
from utils.storage import ImageStorage

UPLOAD_PATH = getattr(settings, 'FEEDFISH_UPLOAD', 'uploads/feedfish')
OPTIONS = {
    'resize_width': 568,
    'resize_height': 321
}


fish_status_choices = (
    ('oops', _('One little fish died.')),
    ('sad', _('More than one fish died.')),
    ('fine', _('They eat a lot.')),
    ('good', _('Better than usual.')),
    ('blooming', _('New baby fish come to the world.')),
    ('not_feed', _("He didn't feed them this time."))
)

action_choices = (
    ('feed', _('Feed fish')),
    ('change_water', _('Change Water'))
)


class FeedFish(TimeStampedModel):
    fish_status = models.CharField(_('fish status'),
                                   max_length=64,
                                   choices=fish_status_choices)
    fish_amount = models.PositiveIntegerField(_('fish count'))
    user = models.ForeignKey(User)
    fish_photo = models.ImageField(_('fish photo'),
                                   blank=True,
                                   upload_to=UPLOAD_PATH,
                                   help_text=_('Photo of fishes.'),
                                   storage=ImageStorage(option=OPTIONS))
    action = models.CharField(_('action'),
                              max_length=64,
                              choices=action_choices)
    remark = models.TextField(_('Remark'),
                              blank=True)

    class Meta:
        verbose_name = _('Feed Fish')
        verbose_name_plural = _('Feed Fish')
        ordering = ['-date_created']
