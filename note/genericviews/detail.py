# coding: utf-8
#
# xiaoyu <xiaokong1937@gmail.com>
#
#
""" Detail Generic Views for note app"""
from django.views.generic.detail import DetailView
from django.db.models import Q

from note.models import Note
from .list import NoteContextMixin


__all__ = ['NoteDetailView']


class NoteDetailView(NoteContextMixin, DetailView):
    model = Note
    slug_field = 'meta_link'
    slug_url_kwarg = 'meta_link'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        previous, next_ = self.get_previous_and_next()
        note_context = self.get_note_context()
        context = self.get_context_data(object=self.object,
                                        previous_note=previous,
                                        next_note=next_,
                                        next=self.object.get_absolute_url(),
                                        **note_context)
        return self.render_to_response(context)

    def get_previous_and_next(self):
        '''
            Get previous and next note by note object.
        '''
        self.queryset = self.get_queryset()
        if self.request.user.is_authenticated():
            previous = self.queryset.filter(Q(user__id=self.object.user.id),
                                            Q(id__lt=self.object.id),
                                            Q(is_valid=True),
                                            Q(is_private=False) |
                                            Q(is_private=True) &
                                            Q(user__id=self.request.user.id))
            next_ = self.queryset.filter(Q(user__id=self.object.user.id),
                                         Q(id__gt=self.object.id),
                                         Q(is_valid=True),
                                         Q(is_private=False) |
                                         Q(is_private=True) &
                                         Q(user__id=self.request.user.id))
        else:
            previous = self.queryset.filter(user__id=self.object.user.id,
                                            id__lt=self.object.id,
                                            is_valid=True,
                                            is_private=False)
            next_ = self.queryset.filter(user__id=self.object.user.id,
                                         id__gt=self.object.id,
                                         is_valid=True,
                                         is_private=False)
        next_ = next_.order_by('date_created')
        previous = previous.order_by('-date_created')
        previous_object = previous[0] if previous else None
        next_object = next_[0] if next_ else None
        return (previous_object, next_object)
