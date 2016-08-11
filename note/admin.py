# coding: utf-8
#
# xiaoyu <xiaokong1937@gmail.com>
#
# 2014/02/05
#
# admin for note app.
#
from django import forms
from django.contrib import admin
from django.contrib.contenttypes import generic

from .models import Note, TaggedItem, Category
from utils.mixin import LimitUserMixin, SimditorMixin


class NoteForm(forms.ModelForm):

    class Meta:
        model = Note
        widgets = {
            'content': forms.Textarea(attrs={'id': 'editor'})
        }


class TagsInline(generic.GenericTabularInline):
    model = TaggedItem


class CategoryAdmin(LimitUserMixin, admin.ModelAdmin):
    date_hierarchy = 'date_created'
    fields = ('name',)
    model = Category


class NoteAdmin(LimitUserMixin, SimditorMixin, admin.ModelAdmin):
    date_hierarchy = 'date_modified'
    fields = ('title', 'content', 'category', 'meta_link',
              'is_private', 'is_rst', 'enable_comments')
    inlines = [
        TagsInline,
    ]
    form = NoteForm
    list_display = ('title', 'category',
                    'is_private', 'enable_comments',
                    'display_created_date')
    list_editable = ('category', 'enable_comments', 'is_private')

    list_filter = ('category', 'is_private',
                   'enable_comments', 'is_rst')
    search_fields = ['title', 'content']
    ordering = ('-date_created', )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'category':
            kwargs['queryset'] = Category.objects.filter(user=request.user,
                                                         is_valid=True)
            return super(NoteAdmin, self).formfield_for_foreignkey(
                db_field, request, **kwargs)


admin.site.register(Note, NoteAdmin)
admin.site.register(Category, CategoryAdmin)
