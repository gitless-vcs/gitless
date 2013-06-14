#!/usr/bin/python

"""gl-commit - Record changes in the local repository.

Implements the gl-commit command, part of the Gitless suite.
"""

import argparse
import os

import commit_dialog
import lib


def main():
  parser = argparse.ArgumentParser(
      description="Record changes in the local repository")
  parser.add_argument(
      'only_files', nargs='*',
      help='Only the files listed as arguments will be committed (files could '
           'be tracked or untracked files)')
  parser.add_argument(
      '-exc', '--exclude', nargs='+',
      help=('Files listed as arguments will be excluded from the commit (files '
            'must be tracked files)'),
      dest='exc_files')
  parser.add_argument(
      '-inc', '--include', nargs='+',
      help=('Files listed as arguments will be included to the commit (files '
            'must be untracked files)'),
      dest='inc_files')
  parser.add_argument(
      '-m', '--message',
      help='Commit message',
      dest='m')
  args = parser.parse_args()

  # TODO(sperezde): re-think this worflow a bit.

  only_files = frozenset(args.only_files)
  exc_files = frozenset(args.exc_files) if args.exc_files else []
  inc_files = frozenset(args.inc_files) if args.inc_files else []

  if not _valid_input(only_files, exc_files, inc_files):
    print 'An error was encountered'
    return

  commit_files = _compute_fs(only_files, exc_files, inc_files)

  if not commit_files:
    print 'No files to commit'
    return

  msg = args.m
  if not msg:
    # Show the commit dialog.
    msg, commit_files = commit_dialog.show(commit_files)
    if not msg.strip():
      print 'No commit message provided'
      return
    if not commit_files:
      print 'No files to commit'
      return
    if not _valid_input(commit_files, [], []):
      print 'An error was encountered'
      return

  _auto_track(commit_files)
  print lib.commit(commit_files, msg)


def _valid_input(only_files, exc_files, inc_files):
  """Validates user input.

  This function will print to stdout in case user-provided values are invalid
  (and return False).

  Args:
    only_files: user-provided list of filenames to be committed only.
    exc_files: list of filenames to be excluded from commit.
    inc_files: list of filenames to be included to the commit.

  Returns:
    True if the input is valid, False if otherwise.
  """
  if only_files and (exc_files or inc_files):
    print (
        'You provided a list of filenames to be committed only but also '
        'provided a list of files to be excluded or included.')
    return False

  ret = True
  for fp in only_files:
    if not os.path.exists(fp):
      print 'File %s doesn\'t exist' % fp
      ret = False

  for fp in exc_files:
    # We check that the files to be excluded are existing tracked files.
    # TODO(sperezde): check that they are also modified.
    if not os.path.exists(fp):
      print 'File %s doesn\'t exist' % fp
      ret = False
    elif not lib.is_tracked_file(fp):
      print (
          'File %s, listed to be excluded from commit, is not a tracked file.' % fp)
      ret = False

  for fp in inc_files:
    # We check that the files to be included are existing untracked files.
    if not os.path.exists(fp):
      print 'File %s doesn\'t exist' % fp
      ret = False
    elif lib.is_tracked_file(fp):
      print (
          'File %s, listed to be included in the commit, is not a untracked '
          'file.' % fp)
      ret = False

  return ret


def _compute_fs(only_files, exc_files, inc_files):
  """Compute the final fileset to commit.
  
  Args:
    only_files: list of filenames to be committed only.
    exc_files: list of filenames to be excluded from commit.
    inc_files: list of filenames to be included to the commit.

  Returns:
    A list of filenames to be committed.
  """
  # TODO(sperezde): this should be case-sensitive or not depending on the OS.
  if only_files:
    ret = only_files
  else:
    tracked_modified, unused_untracked = lib.repo_status()
    # TODO(sperezde): push the use of frozenset to the library.
    ret = frozenset(tm[0] for tm in tracked_modified)
    ret = ret.difference(exc_files)
    ret = ret.union(inc_files)

  return ret


def _auto_track(files):
  """Tracks those untracked files in the list."""
  for f in files:
    if not lib.is_tracked_file(f):
      lib.track_file(f)


if __name__ == '__main__':
  main()
