# coding: utf-8

from django import template


register = template.Library()


@register.filter(name='addcss')
def addcss(field, css):
    return field.as_widget(attrs={'class': css})


@register.filter(name='to_class_name')
def to_class_name(value):
    return value.__class__.__name__


@register.filter(name='to_app_label')
def to_app_label(value):
    return value._meta.app_label


@register.filter
def percentage(value):
    return format(value, ".2%")
