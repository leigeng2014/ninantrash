#!/usr/bin/env python
# coding: utf-8
#
# xiaoyu <xiaokong1937@gmail.com>
#
# Custom Storage for ImageFile management.
#
from PIL import Image
from StringIO import StringIO

from django.contrib.staticfiles.storage import CachedFilesMixin

from baniu.django.storage import Storage


class CachedQiniuStorage(CachedFilesMixin, Storage):
    pass


class ImageStorage(Storage):
    '''
    Resize image, reduce qulity.
    '''
    def __init__(self, *args, **kwargs):
        self.option = kwargs.setdefault('option', {})
        kwargs.pop('option')
        super(ImageStorage, self).__init__(*args, **kwargs)

    def _save(self, name, content):
        output = StringIO()
        im = Image.open(content)
        width, height = im.size
        resize_width = self.option.get('resize_width', width / 2)
        resize_height = self.option.get('resize_height', height / 2)
        qulity = self.option.get('qulity', 70)
        im = im.resize((resize_width, resize_height), Image.ANTIALIAS)
        format = im.format or 'PNG'
        im.save(output, format=format, qulity=qulity)
        return super(ImageStorage, self)._save(name, output.getvalue())
