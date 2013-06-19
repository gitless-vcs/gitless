#!/usr/bin/python

"""gl-status - Show the status of files in the repo.

Implements the gl-status command, part of the Gitless suite. The gl-status
command allows the user to retrieve the status of the files in the repo.
"""

import argparse

import branch_lib
import cmd
import lib
import pprint
import sync_lib


def main():
  parser = argparse.ArgumentParser(
      description="Show status of the repo")

  _print('On branch %s' % branch_lib.current())

  in_merge = sync_lib.merge_in_progress()
  if in_merge:
    _print_blank()
    _print_merge_exp()

  _print_blank()
  _print('Tracked files with modifications:')
  _print_exp('these will be automatically considered for commit')
  _print_exp(
      'use gl untrack <f> if you don\'t want to track changes to file f')
  _print_blank()
  tracked_mod_list, untracked_list = lib.repo_status()
  if not tracked_mod_list:
    print '#     There are no tracked files with modifications to list'
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
      elif in_merge and sync_lib.was_resolved(fp):
        str = ' (conflicts resolved)'
      _print_file(fp, str)
  _print_blank()
  _print_blank()
  _print('Untracked files:')
  _print_exp('these won\'t be considered for commit')
  _print_exp('use gl track <f> if you want to track changes to file f')
  _print_blank()
  if not untracked_list:
    print '#     There are no untracked files to list'
  else:
    for fp, exists_in_lr in untracked_list:
      _print_file(fp, ' (exists in local repo)' if exists_in_lr else '')


def _print_blank():
  print '#'


def _print(s):
  print '# %s' % s


def _print_exp(s):
  print '#   (%s)' % s


def _print_file(fp, msg):
  print '#     %s%s' % (fp, msg)


def _print_merge_exp():
  pprint.msg(
      'You are in the middle of a merge; all conflicts must be resolved before '
      'commiting')
  pprint.exp('use gl merge --abort to go back to the state before the merge')
  pprint.exp('use gl resolve <f> to mark file f as resolved')
  pprint.exp('once you solved all conflicts do gl commit to complete the merge')
  pprint.blank()


if __name__ == '__main__':
  cmd.run(main)
