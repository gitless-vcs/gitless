# Gitless - a version control system built on top of Git.
# Copyright (c) 2013  Santiago Perez De Rosso.
# Licensed under GNU GPL, version 2.

"""gl status - Show the status of files in the repo."""


from gitless.core import branch as branch_lib
from gitless.core import file as file_lib
from gitless.core import repo as repo_lib
from gitless.core import sync as sync_lib

import pprint


def parser(subparsers):
  """Adds the status parser to the given subparsers object."""
  status_parser = subparsers.add_parser(
      'status', help='show status of the repo')
  status_parser.set_defaults(func=main)


def main(unused_args):
  pprint.msg(
      'On branch {}, repo-directory /{}'.format(
          branch_lib.current(), repo_lib.cwd()))

  in_merge = sync_lib.merge_in_progress()
  in_rebase = sync_lib.rebase_in_progress()
  if in_merge:
    pprint.blank()
    _print_conflict_exp('merge')
  elif in_rebase:
    pprint.blank()
    _print_conflict_exp('rebase')

  tracked_mod_list = []
  untracked_list = []
  for f in file_lib.status_all():
    if f.type == file_lib.TRACKED and f.modified:
      tracked_mod_list.append(f)
    elif f.type == file_lib.UNTRACKED:
      untracked_list.append(f)
  pprint.blank()
  tracked_mod_list.sort(key=lambda f: f.fp)
  _print_tracked_mod_files(tracked_mod_list)
  pprint.blank()
  pprint.blank()
  untracked_list.sort(key=lambda f: f.fp)
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
    for f in tracked_mod_list:
      exp = ''
      # TODO(sperezde): sometimes files don't appear here if they were resolved.
      if not f.exists_in_lr:
        exp = ' (new file)'
      elif not f.exists_in_wd:
        exp = ' (deleted)'
      elif f.in_conflict:
        exp = ' (with conflicts)'
      elif f.resolved:
        exp = ' (conflicts resolved)'
      pprint.item(f.fp, opt_msg=exp)


def _print_untracked_files(untracked_list):
  pprint.msg('Untracked files:')
  pprint.exp('these won\'t be considered for commit')
  pprint.exp('use gl track <f> if you want to track changes to file f')
  pprint.blank()
  if not untracked_list:
    pprint.item('There are no untracked files to list')
  else:
    for f in untracked_list:
      s = ''
      if f.exists_in_lr:
        if f.exists_in_wd:
          s = ' (exists in local repo)'
        else:
          s = ' (exists in local repo but not in working directory)'
      pprint.item(f.fp, opt_msg=s)


def _print_conflict_exp(t):
  pprint.msg(
      'You are in the middle of a {0}; all conflicts must be resolved before '
      'commiting'.format(t))
  pprint.exp(
      'use gl {0} --abort to go back to the state before the {0}'.format(t))
  pprint.exp('use gl resolve <f> to mark file f as resolved')
  pprint.exp('once you solved all conflicts do gl commit to continue')
  pprint.blank()
