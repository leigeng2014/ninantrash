#!/usr/bin/env python
# coding: utf-8
#
# xiaoyu <xiaokong1937@gmail.com>
#
# 2014/02/13
#

from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.contrib.auth.models import User
from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.contenttypes import generic

from utils.storage import ImageStorage
from utils.model_utils import TimeStampedModel
from backends.models import Event

UPLOAD_PATH = getattr(settings, 'REDACTOR_UPLOAD', 'uploads/')
MEDIA_ROOT = getattr(settings, 'MEDIA_URL', '/upload/')


class WeixinMp(TimeStampedModel):
    title = models.CharField(verbose_name=_('title'), max_length=128,
                             unique=True)
    content = models.TextField(verbose_name=_('content'))
    digest = models.CharField(verbose_name=_('digest'),
                              max_length=255, null=True, blank=True)
    user = models.ForeignKey(User, verbose_name=_('author'))
    fileid = models.CharField(verbose_name=_('fileid'), max_length=32)
    show_cover_pic = models.BooleanField(verbose_name=_('show cover image'),
                                         default=True)

    cover_img = models.ImageField(verbose_name=_('Cover Image'),
                                  upload_to=UPLOAD_PATH,
                                  blank=True,
                                  help_text=_('Cover Image for article, will '
                                              'be set to `uploads/cover.jpg`'
                                              ' if left blank.'),
                                  storage=ImageStorage())

    is_published = models.BooleanField(_('is_published'), default=False)
    sync = models.BooleanField(_('Sync'), default=True,
                               help_text=_('Synchronize to weixin server.'))

    events = generic.GenericRelation(Event)

    class Meta:
        verbose_name = _('weinxin_article')
        verbose_name_plural = _('weixin_articles')
        ordering = ["-date_created"]

    def get_digest(self):
        """ Return weixinmp desciption."""
        return self.digest or self.content[:200]

    def get_description(self):
        """ Proxy for get_digest. """
        return self.get_digest()

    def get_resource(self):
        """ Helper function for timeline. """
        msg = _("wrote a new wechat article : %(title)s") % {
            'title': self.title}
        msg = unicode(msg)
        resource = {
            'title': msg,
            'description': self.get_digest(),
            'url': self.get_absolute_url(),
            'image_url': self.cover_img.url,
        }
        return resource

    def __unicode__(self):
        return self.title

    def display_created_date(self):
        return timezone.localtime(self.date_created)
    display_created_date.short_description = _('Time created')

    def get_absolute_url(self):
        """ Return absolute url."""
        return reverse('weixin.views.detail', args=(self.id,))

    def save(self,  *args,  **kwargs):
        """ Auto add timestamp when saved."""
        created = not self.id
        if not self.digest:
            self.digest = self.get_digest()
        if not self.cover_img:
            self.cover_img = getattr(settings, 'WEIXIN_DEFAULT_COVER')
            self.fileid = getattr(settings, 'WEIXIN_DEFAULT_COVER_ID')
        super(WeixinMp, self).save(*args, **kwargs)

        if self.sync and created:
            from sae.taskqueue import add_task
            task_link = reverse('weixinmp.upload', args=(self.pk,))
            add_task('weixin', task_link, delay=300)
            task_link = reverse('weixinmp.image_collect', args=(self.pk,))
            add_task('weixin', task_link, delay=180)

        if created:
            event = Event(user=self.user, content_object=self)
            event.save()

weixin_content_types = (
    ('subscribe', _('Message for user subscribe')),
    ('express_usage', _('Usage for express')),
    ('commen_usage', _('Usage for commen')),
)


class WeixinConfig(TimeStampedModel):
    user = models.ForeignKey(User)
    trigger_type = models.CharField(verbose_name=_('trigger type'),
                                    max_length=128,
                                    choices=weixin_content_types,
                                    unique=True)
    content = models.TextField(verbose_name=_('content'))

    class Meta:
        verbose_name = _('weixin_config')
        verbose_name_plural = _('weixin_configs')
        ordering = ["-date_created"]

    def __unicode__(self):
        return self.trigger_type


match_type_choices = (
    ('partly', _('trigger keyword partly match')),
    ('entirely', _('trigger keyword entirely match')),
)


class WeixinReply(TimeStampedModel):
    user = models.ForeignKey(User)
    trigger = models.CharField(verbose_name=_('Keyword'),
                               max_length=254,
                               unique=True)
    content = models.TextField(verbose_name=_('content'))
    match_type = models.CharField(verbose_name=_('match_type'),
                                  choices=match_type_choices,
                                  max_length=254)

    class Meta:
        verbose_name = _('weixin_reply')
        verbose_name_plural = _('weixin_replies')
        ordering = ["-date_created"]

    def __unicode__(self):
        return self.trigger


class WeixinGlobalConfig(models.Model):
    last_article = models.PositiveIntegerField(
        verbose_name=_('last article id'), default=0)
    article_to_pub = models.PositiveIntegerField(
        verbose_name=_('unpublished article id'), default=0)

    class Meta:
        verbose_name = _('weixin_global_config')
        verbose_name_plural = _('weixin_global_config')

    def __unicode__(self):
        return self._meta.verbose_name


class WeixinUser(models.Model):
    nickname = models.CharField(verbose_name=_('nickname'),
                                max_length=32)
    fakeid = models.CharField(verbose_name=_('fake_id'),
                              max_length=32)
    openid = models.CharField(verbose_name=_('openid'),
                              max_length=32)
    last_msg_time = models.DateTimeField(editable=False,
                                         verbose_name=_('last msg send time'))

    class Meta:
        verbose_name = _('weixin_user')
        verbose_name_plural = _('weixin_users')

    def __unicode__(self):
        return self.nickname

    def save(self,  *args,  **kwargs):
        """ Auto add timestamp when saved."""
        if not self.id:
            self.last_msg_time = timezone.now()
        super(WeixinUser, self).save(*args, **kwargs)
