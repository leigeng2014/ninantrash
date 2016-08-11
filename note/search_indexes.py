# coding: utf-8
#
# xiaoyu <xiaokong1937@gmail.com>
#
# 2015/02/02
#
"""
Haystack indexes.

"""
from haystack import indexes

from .models import Note


class NoteIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        return Note

    def get_updated_field(self):
        return 'date_modified'

    def index_queryset(self, using=None):
        return self.get_model().objects.filter(is_valid=True, is_private=False)
