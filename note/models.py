# coding: utf-8
#
# xiaoyu <xiaokong1937@gmail.com>
#
# 2014/01/16
#
# models for note app
#
""" Models for note app ."""
import re

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.core import validators
from django.db import models
from django.utils.timezone import localtime
from django.utils.translation import ugettext_lazy as _


from utils import bd_pingback
from utils.model_utils import TimeStampedModel
from south.modelsinspector import add_introspection_rules
from backends.models import Event, Counter
from tastypie.models import create_api_key


models.signals.post_save.connect(create_api_key, sender=User)


class TaggedItem(models.Model):
    tag = models.CharField(_('Tag'), max_length=64)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    def __unicode__(self):
        return self.tag

    class Meta:
        verbose_name = _('taggeditem')
        verbose_name_plural = _('taggeditems')


class Category(TimeStampedModel):
    user = models.ForeignKey(User)
    name = models.CharField(verbose_name=_('category'), max_length=256)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('categories')

    def get_absolute_url(self):
        return reverse('note.category.detail', args=(self.id,))


class Note(TimeStampedModel):
    user = models.ForeignKey(User)
    title = models.CharField(verbose_name=_('title'), max_length=256)
    content = models.TextField(verbose_name=_('content'))

    tags = generic.GenericRelation(TaggedItem)
    category = models.ForeignKey(Category, verbose_name=_('category'))

    enable_comments = models.BooleanField(_('allow_comment'), default=True)
    is_rst = models.BooleanField(_('wrote in reStructuredText'),
                                 default=False)

    meta_link = models.CharField(
        _('title_url'), max_length=254,
        help_text=_('Link of the note. Leave blank if you want to use the '
                    'Pinyin of title. Letters, numbers and '
                    ' /./+/-/ characters'),
        validators=[
            validators.RegexValidator(re.compile('^[\w\s.+-]+$'),
                                      _('Enter a valid title link.'),
                                      'invalid')
        ])

    events = generic.GenericRelation(Event)

    class Meta:
        verbose_name = _('note')
        verbose_name_plural = _('notes')
        ordering = ["-date_modified"]

    def get_description(self):
        """ Return note desciption."""
        return self.content[:200]

    def get_tags(self):
        '''
            Get Tags from TaggedItem.
        '''
        note_type = ContentType.objects.get_for_model(self)
        tags = TaggedItem.objects.filter(content_type__pk=note_type.id,
                                         object_id=self.id)
        return tags

    def __unicode__(self):
        return self.title

    def hits(self):
        note_type = ContentType.objects.get_for_model(self)
        counter, created = Counter.objects.get_or_create(
            content_type=note_type,
            object_id=self.id)
        return counter.count

    def display_created_date(self):
        return localtime(self.date_created)
    display_created_date.short_description = _('Time created')

    def get_absolute_url(self):
        """ Return absolute url."""
        return reverse('note.views.detail', args=(self.meta_link,))

    def get_resource(self):
        """ Helper function for timeline. """
        msg = _("wrote a new note : %(title)s") % {'title': self.title}
        msg = unicode(msg)
        resource = {
            'title': msg,
            'description': self.get_description(),
            'url': self.get_absolute_url(),
        }
        return resource

    def save(self,  *args,  **kwargs):
        """ Auto add timestamp when saved."""
        self.meta_link = re.sub(r'\W', '-', self.meta_link)
        created = not self.id

        super(Note, self).save(*args, **kwargs)
        # Change since 2014/04/02 . Signal was canceled.
        if not self.is_private and not settings.DEBUG:
            try:
                bd_pingback.pingback(self)
            except Exception:
                pass

        # Add timeline update.
        if created:
            event = Event(user=self.user, content_object=self)
            event.save()

        # Add task to taskqueue for search indexes update.
        from sae.taskqueue import add_task
        add_task('task1', '/backends/updateindex/')


# South custom field fix.
add_introspection_rules([], ['^utils\.model_utils\.AutoCreatedField',
                             '^utils\.model_utils\.AutoLastModifiedField',
                             '^redactor.fields.RedactorField'])
