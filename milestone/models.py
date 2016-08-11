#!/usr/bin/env python
# coding: utf-8
#
# xiaoyu <xiaokong1937@gmail.com>
#
# 2014/05/17
#
"""
Models for milestone app.

"""
import json

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.db.models import Sum
from django.dispatch import receiver
from django.db.models.signals import m2m_changed
from django.contrib.contenttypes import generic
from django.core.urlresolvers import reverse

from utils.model_utils import TimeStampedModel
from backends.models import Event


stone_status = (
    ("ongoing", _("Milestone is ongoning")),
    ("finished", _("Milestone has been finished.")),
    ("aborted", _("Milestone has been aborted.")),
)


class Stone(TimeStampedModel):
    base_score = models.IntegerField(
        verbose_name=_("base score"),
        default=0,
        help_text=_("Base score for your milestone. Can be negetive."))
    achieve_score = models.IntegerField(
        verbose_name=_("achieve score"),
        default=2888,
        help_text=_("Final score for your milestone. If a milestone's score"
                    " reached its `achieve_score`, the milestone will be"
                    " marked as `complished`."))
    title = models.CharField(
        verbose_name=_("title"),
        max_length=64,
        help_text=_("The title of your milestone."))
    description = models.TextField(verbose_name=_("description"))
    status = models.CharField(
        verbose_name=_("status"),
        default="ongoing",
        max_length=64,
        help_text=_("Status of your milestone."),
        choices=stone_status)
    user = models.ForeignKey(User)

    events = generic.GenericRelation(Event)

    @property
    def current_score(self):
        if self.status == 'finished':
            return self.achieve_score
        total_score = self.thing_set.aggregate(total=Sum('score'))['total']
        return total_score or 0

    def get_absolute_url(self):
        return reverse('milestone.detailview', args=(self.id,))

    @property
    def percentage(self):
        return float(self.current_score) / float(self.achieve_score)

    def __unicode__(self):
        return self.title

    def get_resource(self):
        msg = _("started a new milestone : %(title)s") % {
            'title': self.title}
        msg = unicode(msg)
        resource = {
            'title': msg,
            'description': self.description,
            'url': self.get_absolute_url(),
        }
        return resource

    class Meta:
        verbose_name = _("milestone")
        verbose_name_plural = _("milestones")

    def save(self, *args, **kwargs):
        created = not self.id
        super(Stone, self).save(*args, **kwargs)
        if created:
            event = Event(user=self.user, content_object=self)
            event.save()


class Thing(TimeStampedModel):
    name = models.CharField(verbose_name=_("name"), max_length=64)
    score = models.IntegerField(verbose_name=_("score"), default=10)
    stone = models.ManyToManyField(Stone, verbose_name=_("milestone"))
    user = models.ForeignKey(User)

    class Meta:
        verbose_name = _("thing")
        verbose_name_plural = _("things")


@receiver(m2m_changed, sender=Thing.stone.through, dispatch_uid='thing_42')
def update_stone_status(sender, instance, action, **kwargs):
    if action == 'post_add':
        for stone in instance.stone.all():
            if stone.current_score >= stone.achieve_score:
                if stone.staus == 'finished':
                    return
                stone.status = 'finished'
                stone.save()
                msg = _("%(user)s achieved a new milestone : %(title)s") % {
                    'user': stone.user.username,
                    'title': stone.title}
                msg = unicode(msg)
                resource = stone.get_resource()
                resource.update({'title': msg})
                resource = json.dumps(resource)
                event = Event(user=stone.user, content_object=stone,
                              resourse=resource)
                event.save()
