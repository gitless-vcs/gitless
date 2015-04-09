# -*- coding: utf-8 -*-
# Gitless - a version control system built on top of Git.
# Licensed under GNU GPL v2.

"""gl merge - Merge the divergent changes of one branch onto another."""


from __future__ import unicode_literals

from . import sync_cmd


parser = sync_cmd.parser('merge')
