#!/usr/bin/python

"""gl-commit - Record changes in the local repository.

Implements the gl-commit command, part of the Gitless suite.
"""

import argparse
import os

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

  only_files = frozenset(args.only_files)
  exc_files = frozenset(args.exc_files) if args.exc_files else []
  inc_files = frozenset(args.inc_files) if args.inc_files else []

  if not valid_input(only_files, exc_files, inc_files):
    print 'An error was encountered.'
    return

  if args.m:
    # The user provided a message, all ready to commit.
    commit_files = compute_fs(only_files, exc_files, inc_files)

    if not commit_files:
      print 'No files to commit'
      return

    print lib.commit(commit_files, args.m)
  else:
    # Show the commit dialog.
    print 'TODO: show the dialog'
   

def valid_input(only_files, exc_files, inc_files):
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
          'File %s, listed to be excluded from commit, is not a tracked file.')
      ret = False

  for fp in inc_files:
    # We check that the files to be included are existing untracked files.
    if not os.path.exists(fp):
      print 'File %s doesn\'t exist' % fp
      ret = False
    elif lib.is_tracked_file(fp):
      print (
          'File %s, listed to be included in the commit, is not a untracked '
          'file.')
      ret = False

  return ret


def compute_fs(only_files, exc_files, inc_files):
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

  # We auto-track those untracked files listed.
  for f in ret:
    if not lib.is_tracked_file(f):
      lib.track_file(f)

  return ret


if __name__ == '__main__':
  main()
