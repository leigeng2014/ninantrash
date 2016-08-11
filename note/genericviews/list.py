# coding: utf-8
#
# xiaoyu <xiaokong1937@gmail.com>
#
# 2014
#
# List Generic views for ninan.note
#
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _

from endless_pagination.views import AjaxListView

from note.models import Note, TaggedItem, Category
from utils.mixin import (PrivateObjectMixin, NoteContextMixin,
                         AjaxMonthArchiveView)


__all__ = ['BaseNoteListView', 'NoteListView', 'NoteListViewByTag',
           'NoteListViewByCategory', 'NoteListViewByAuthor',
           'NoteListViewByCategory']


class BaseNoteListView(NoteContextMixin, AjaxListView):
    ''' Show note list. '''
    page_title = _('Note List')
    template_name = 'note/note_list.html'
    page_template = 'note/note_list_page.html'

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        note_context = self.get_note_context()

        context_data = self.get_context_data(object_list=self.object_list,
                                             title=self.page_title,
                                             page_template=self.page_template,
                                             **note_context)
        return self.render_to_response(context_data)


class NoteListView(PrivateObjectMixin, BaseNoteListView):
    ''' Show note list. '''

    def get_queryset(self):
        '''
            Get notes.
        '''
        queryset = Note.objects.all()
        return self.filte_private(queryset)


class NoteListViewByTag(NoteListView):
    ''' Show note list by tag. '''

    def get_queryset(self):
        # TODO: Get queryset from content_types. @ 2014/04/14
        queryset = []
        self.tag = self.kwargs.get('tag', None)
        self.page_title = _('Notes tagged as [%(tag)s]') % {'tag': self.tag}
        self.note_type = ContentType.objects.get_for_model(Note)
        tags = TaggedItem.objects.filter(tag=self.tag).order_by('-id')
        for tag in tags:
            note = tag.content_object
            if not note:
                continue
            if note.is_valid is False:
                continue
            if note.is_private is False:
                queryset.append(note)
                continue
            if note.user.id == self.request.user.id:
                queryset.append(note)
        return queryset


class NoteListViewByCategory(NoteListView):
    ''' Show note list by category. '''

    def get_queryset(self):
        queryset = []
        self.catid = self.kwargs.get('catid', None)
        try:
            self.cat = Category.objects.get(pk=self.catid)
        except Category.DoesNotExist:
            self.page_title = _('No notes in category %(cat_id)s '
                                '.') % {'cat_id': self.catid}
            return queryset
        queryset = Note.objects.filter(category=self.cat, is_valid=True)
        self.page_title = _('Notes in category %(cat)s') % {'cat': self.cat}
        return self.filte_private(queryset)


class NoteListViewByAuthor(NoteListView):
    ''' Show note list by author. '''
    def get_queryset(self):
        user = self.kwargs.get('user', '')
        self.page_title = _('Note created by %(author)s') % {'author': user}
        queryset = Note.objects.filter(user__username=user, is_valid=True)
        return self.filte_private(queryset)


class NoteListViewByMonth(NoteContextMixin, PrivateObjectMixin,
                          AjaxMonthArchiveView):
    ''' Show note list by year and month. '''
    date_field = 'date_created'
    make_object_list = True
    queryset = Note.objects.filter(is_valid=True)
    template_name = 'note/note_list.html'

    def get_dated_queryset(self, ordering=None, **lookup):
        self.queryset = super(NoteListViewByMonth,
                              self).get_dated_queryset(ordering, **lookup)
        year = self.kwargs.get('year', '')
        month = self.kwargs.get('month', '')
        self.page_title = _('Notes created in %(year)s - '
                            '%(month)s ') % {'year': year, 'month': month}
        return self.filte_private(self.queryset)

    def get_dated_items(self):
        self.date_list, self.object_list, extra_content = super(
            NoteListViewByMonth, self).get_dated_items()
        extra_content.update({'title': self.page_title})
        note_context = self.get_note_context()
        extra_content.update(note_context)
        return self.date_list, self.object_list, extra_content
