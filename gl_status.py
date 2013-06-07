#!/usr/bin/python

"""gl-status - Show the status of files in the repo.

Implements the gl-status command, part of the Gitless suite. The gl-status
command allows the user to retrieve the status of the files in the repo.
"""

import argparse

import lib


def main():
  parser = argparse.ArgumentParser(
      description="Show status of the repo")
  tracked_mod_list, untracked_list = lib.repo_status()
  _print('On branch TBD')
  _print_blank()
  _print('Tracked files with modifications:')
  _print_exp('these will be automatically considered for commit')
  _print_exp(
      'use gl untrack <f> if you don\'t want to track changes to file f')
  _print_exp('use gl reset <f> to discard changes to file f')
  _print_blank()
  for fp in tracked_mod_list:
    _print_file(fp)
  _print_blank()
  _print_blank()
  _print('Untracked files:')
  _print_exp('these won\'t be considered for commit')
  _print_exp('use gl track <f> if you want to track changes to file f')
  _print_blank()
  for fp in untracked_list:
    _print_file(fp)


def _print_blank():
  print '#'


def _print(s):
  print '# %s' % s


def _print_exp(s):
  print '#   (%s)' % s


def _print_file(fp):
  print '#     %s' % fp


if __name__ == '__main__':
  main()
