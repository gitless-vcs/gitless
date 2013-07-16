# Gitless - a version control system built on top of Git.
# Copyright (c) 2013  Santiago Perez De Rosso.
# Licensed under GNU GPL, version 2.

"""Checks that the Python interpreter version is valid."""


import sys


# [0] -> major
# [1] -> minor
if sys.version_info[0] != 2 or sys.version_info[1] != 7:
  raise Exception('Gitless requires Python 2.7')
