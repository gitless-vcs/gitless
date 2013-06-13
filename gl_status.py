#!/usr/bin/python

"""gl-status - Show the status of files in the repo.

Implements the gl-status command, part of the Gitless suite. The gl-status
command allows the user to retrieve the status of the files in the repo.
"""

import argparse

import branch_lib
import lib


def main():
  parser = argparse.ArgumentParser(
      description="Show status of the repo")
  _print('On branch %s' % branch_lib.current())
  _print_blank()
  _print('Tracked files with modifications:')
  _print_exp('these will be automatically considered for commit')
  _print_exp(
      'use gl untrack <f> if you don\'t want to track changes to file f')
  _print_exp('use gl reset <f> to discard changes to file f')
  _print_blank()
  tracked_mod_list, untracked_list = lib.repo_status()
  if not tracked_mod_list:
    print '#     There are no tracked files with modifications to list'
  else:
    for fp, exists_in_lr in tracked_mod_list:
      _print_file(fp, ' (new file)' if not exists_in_lr else '')
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


if __name__ == '__main__':
  main()
