# coding: utf-8
""" Url configs. """
from django.conf.urls import patterns, url
from django.conf import settings
from django.views.decorators.cache import cache_page

from .genericviews.list import (NoteListView, NoteListViewByTag,
                                NoteListViewByMonth,
                                NoteListViewByAuthor,
                                NoteListViewByCategory)
from .genericviews.detail import NoteDetailView
from core.utils import counter_cache_page
from note.models import Note
from backends.models import counter_add


def note_counter_add(**kwargs):
    metalink = kwargs.get('meta_link')
    try:
        note = Note.objects.get(meta_link=metalink)
    except Note.DoesNotExist:
        return None
    else:
        counter_add(note)

cache_time = getattr(settings, 'NOTE_VIEW_CACHE_TIME', 60 * 60)


urlpatterns = patterns(
    '',
    url(r'^$',
        NoteListView.as_view()),
    url(r'^show/(?P<meta_link>([\w\s.@+-]+))/$',
        counter_cache_page(NoteDetailView.as_view(),
                           note_counter_add),
        name='note.views.detail'),
    url(r'^tag/(?P<tag>.*?)/$',
        cache_page(cache_time)(NoteListViewByTag.as_view())),
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/$',
        cache_page(cache_time)(
            NoteListViewByMonth.as_view(month_format='%m'))),
    url(r'^author/(?P<user>([\w.@+-]+))/$',
        cache_page(cache_time)(NoteListViewByAuthor.as_view())),
    url(r'category/(?P<catid>\d+)/$',
        cache_page(cache_time)(NoteListViewByCategory.as_view()),
        name='note.category.detail'),
)
