# coding: utf-8
#
# xiaoyu <xiaokong1937@gmail.com>
#
# 2014/01/16
#
# models for ninan app
import ntpath
import json

from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from baniu.bucket import Bucket

from utils.model_utils import TimeStampedModel
from core.utils import getNickName


AVATAR_PATH = getattr(settings, 'AVATAR_UPLOAD_PATH', 'avatars/')
AVATAR_THUNMB_PATH = getattr(settings, 'AVATAR_THUNMB_PATH', 'avatar_thumbs/')


# Custom User Profile
class Profile(TimeStampedModel):
    user = models.OneToOneField(User)
    nickname = models.CharField(verbose_name=_('nickname'), max_length=16)
    avatar_thumb = models.ImageField(verbose_name=_('avatar thumb'),
                                     blank=True,
                                     upload_to=AVATAR_PATH)
    avatar = models.ImageField(verbose_name=_('avatar'), blank=True,
                               upload_to=AVATAR_PATH)
    signature = models.CharField(verbose_name=_('signature'),
                                 max_length=256,
                                 blank=True)
    bio = models.TextField(verbose_name=_('biography'), blank=True)

    def __unicode__(self):
        return self.nickname

    def save(self, *args, **kwargs):
        """
        Save profile, make thumb of avatar.

        When avatar image was saved, trigger pfop of qiniu_cdn and save a
        thumb image of avatar.
        """
        avatar_not_changed = False
        if self.pk:
            old_obj = Profile.objects.get(pk=self.pk)
            if old_obj.avatar == self.avatar:
                avatar_not_changed = True
        super(Profile, self).save(*args, **kwargs)
        if avatar_not_changed:
            return super(Profile, self).save(*args, **kwargs)
        bucket_name = getattr(settings, 'STORAGE_BUCKET_NAME')
        apikey = getattr(settings, 'STORAGE_ACCESSKEY')
        apisecret = getattr(settings, 'STORAGE_SECRETKEY')
        domain = getattr(settings, 'STORAGE_DOMAIN')
        bucket = Bucket(bucket_name, apikey, apisecret, domain)

        avatar_thumb_height = 64
        avatar_thumb_width = 64
        avatar_url = bucket.generate_url(self.avatar.name)
        ops_url = "{}?imageView2/2/w/{}/h/{}".format(
            avatar_url,
            avatar_thumb_width, avatar_thumb_height)

        def path_leaf(path):
            head, tail = ntpath.split(path)
            return tail or ntpath.basename(head)

        filename = path_leaf(self.avatar.name)
        fname, ext = filename.split('.')
        save_name = '{}{}_thumb.{}'.format(AVATAR_THUNMB_PATH, fname, ext)
        bucket.save_as(ops_url, save_name)
        self.avatar_thumb = save_name
        super(Profile, self).save(*args, **kwargs)


class Event(TimeStampedModel):
    user = models.ForeignKey(User)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    resourse = models.TextField(verbose_name=_('resource'), blank=True)

    def __unicode__(self):
        return unicode(_("%(user)s status") % {'user': self.user.username})

    @property
    def resource(self):
        """
        Title, description, url, image_url.
        A content_object should have a method named get_resource(), which
        should return a dict containing these keys :
            title: the title for this event;
            description: description for content_object;
            url: absolute url for content_object;
            image_url: image or cover image url for content_object;

        """
        if self.resourse:
            return json.loads(self.resourse)
        ob = self.content_object
        if hasattr(ob, 'get_resource'):
            return ob.get_resource()
        return None

    @property
    def nickname(self):
        return getNickName(self.user.username)

    class Meta:
        verbose_name = _('event')
        verbose_name_plural = _('events')


class Counter(TimeStampedModel):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    count = models.PositiveIntegerField(default=1)

    def __unicode__(self):
        return "{}_{}".format(self.content_type, self.count)


def counter_add(obj, *args, **kwrags):
    obj_type = ContentType.objects.get_for_model(obj)
    counter, created = Counter.objects.get_or_create(
        content_type=obj_type,
        object_id=obj.id
    )
    counter.count += 1
    counter.save()
