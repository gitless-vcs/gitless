# -*- coding: utf-8 -*-
# Gitless - a version control system built on top of Git.
# Licensed under GNU GPL v2.

"""gl track - Start tracking changes to files."""


from __future__ import unicode_literals

from . import file_cmd


parser = file_cmd.parser('start tracking changes to files', 'track')
