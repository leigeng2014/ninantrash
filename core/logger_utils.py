#!/usr/bin/env python
# coding: utf-8
#
# xiaoyu <xiaokong1937@gmail.com>
#
# 2014/04/02
#
"""
Logger for ninan project.

In your settings.py, add a logger named `scripts`.

"""
import logging


__all__ = ['logger']

logger = logging.getLogger('scripts')
