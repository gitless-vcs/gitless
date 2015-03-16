# -*- coding: utf-8 -*-
# Gitless - a version control system built on top of Git.
# Licensed under GNU GPL v2.

"""Some helpers for commands."""


from __future__ import unicode_literals

import argparse
import os


def get_branch_name(branch):
  try:
    return branch.remote_name + '/' + branch.branch_name
  except AttributeError:
    return branch.branch_name


def get_branch(branch_name, repo):
  b = repo.lookup_branch(branch_name)
  if not b:
    if '/' not in branch_name:
      raise ValueError('Branch "{0}" doesn\'t exist'.format(branch_name))

    # It might be a remote branch
    remote, remote_branch = branch_name.split('/', 1)
    try:
      r = repo.remotes[remote]
    except KeyError:
      raise ValueError(
          'Remote "{0}" doesn\'t exist, and there is no local '
          'branch "{1}"'.format(remote, branch_name))

    b = r.lookup_branch(remote_branch)
    if not b:
      raise ValueError('Branch "{0}" doesn\'t exist in remote "{1}"'.format(
          remote_branch, remote))
  return b


class PathProcessor(argparse.Action):

  def __call__(self, parser, namespace, paths, option_string=None):
    setattr(namespace, self.dest, self.__process_path(paths))

  def __process_path(self, paths):
    for path in paths:
      if os.path.isdir(path):
        for curr_dir, _, fps in os.walk(path):
          for fp in fps:
            yield os.path.join(curr_dir, fp)
      else:
        yield path
