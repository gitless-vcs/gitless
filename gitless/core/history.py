# Gitless - a version control system built on top of Git.
# Copyright (c) 2013  Santiago Perez De Rosso.
# Licensed under GNU GPL, version 2.

"""Gitless's history lib."""


from gitpylib import log as git_log


def show(verbose=False):
  if verbose:
    git_log.log_p()
  else:
    git_log.log()
