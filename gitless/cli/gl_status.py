# Gitless - a version control system built on top of Git.
# Copyright (c) 2013  Santiago Perez De Rosso.
# Licensed under GNU GPL, version 2.

"""gl status - Show the status of files in the repo."""


import os

from gitless.core import branch as branch_lib
from gitless.core import repo as repo_lib
from gitless.core import sync as sync_lib

import pprint


def parser(subparsers):
  """Adds the status parser to the given subparsers object."""
  status_parser = subparsers.add_parser(
      'status', help='show status of the repo')
  status_parser.set_defaults(func=main)


def main(args):
  pprint.msg(
      'On branch {}, repo-directory {}'.format(
          branch_lib.current(), repo_lib.cwd()))

  in_merge = sync_lib.merge_in_progress()
  in_rebase = sync_lib.rebase_in_progress()
  if in_merge:
    pprint.blank()
    _print_conflict_exp('merge')
  elif in_rebase:
    pprint.blank()
    _print_conflict_exp('rebase')

  tracked_mod_list, untracked_list = repo_lib.status()
  pprint.blank()
  _print_tracked_mod_files(tracked_mod_list)
  pprint.blank()
  pprint.blank()
  _print_untracked_files(untracked_list)
  return True


def _print_tracked_mod_files(tracked_mod_list):
  pprint.msg('Tracked files with modifications:')
  pprint.exp('these will be automatically considered for commit')
  pprint.exp(
      'use gl untrack <f> if you don\'t want to track changes to file f')
  pprint.exp(
      'if file f was committed before, use gl checkout <f> to discard '
      'local changes')
  pprint.blank()
  if not tracked_mod_list:
    pprint.item('There are no tracked files with modifications to list')
  else:
    for fp, exists_in_lr, exists_in_wd, in_conflict in tracked_mod_list:
      str = ''
      # TODO(sperezde): sometimes files don't appear here if they were resolved.
      if not exists_in_lr:
        str = ' (new file)'
      elif not exists_in_wd:
        str = ' (deleted)'
      elif in_conflict:
        str = ' (with conflicts)'
      elif sync_lib.was_resolved(fp):
        str = ' (conflicts resolved)'
      pprint.item(fp, opt_msg=str)


def _print_untracked_files(untracked_list):
  pprint.msg('Untracked files:')
  pprint.exp('these won\'t be considered for commit')
  pprint.exp('use gl track <f> if you want to track changes to file f')
  pprint.blank()
  if not untracked_list:
    pprint.item('There are no untracked files to list')
  else:
    for fp, exists_in_lr, exists_in_wd in untracked_list:
      s = ''
      if exists_in_lr:
        if exists_in_wd:
          s = ' (exists in local repo)'
        else:
          s = ' (exists in local repo but not in working directory)'
      pprint.item(fp, opt_msg=s)


def _print_conflict_exp(t):
  pprint.msg(
      'You are in the middle of a {0}; all conflicts must be resolved before '
      'commiting'.format(t))
  pprint.exp(
      'use gl {0} --abort to go back to the state before the {0}'.format(t))
  pprint.exp('use gl resolve <f> to mark file f as resolved')
  pprint.exp('once you solved all conflicts do gl commit to continue')
  pprint.blank()
