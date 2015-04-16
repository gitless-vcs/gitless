# -*- coding: utf-8 -*-
# Gitless - a version control system built on top of Git.
# Licensed under GNU GPL v2.

"""gl commit - Record changes in the local repository."""


from __future__ import unicode_literals

from gitless import core

from . import commit_dialog
from . import helpers, pprint


def parser(subparsers):
  """Adds the commit parser to the given subparsers object."""
  commit_parser = subparsers.add_parser(
      'commit', help='record changes in the local repository')
  commit_parser.add_argument(
      'only_files', nargs='*',
      help='only the files listed as arguments will be committed (files could '
           'be tracked or untracked files)', action=helpers.PathProcessor)
  commit_parser.add_argument(
      '-e', '--exclude', nargs='+',
      help=('files listed as arguments will be excluded from the commit (files '
            'must be tracked files)'),
      dest='exc_files', action=helpers.PathProcessor)
  commit_parser.add_argument(
      '-i', '--include', nargs='+',
      help=('files listed as arguments will be included to the commit (files '
            'must be untracked files)'),
      dest='inc_files', action=helpers.PathProcessor)
  commit_parser.add_argument(
      '-m', '--message', help='Commit message', dest='m')
  commit_parser.set_defaults(func=main)


def main(args, repo):
  only_files = frozenset(args.only_files)
  exc_files = frozenset(args.exc_files if args.exc_files else [])
  inc_files = frozenset(args.inc_files if args.inc_files else [])

  curr_b = repo.current_branch
  if not _valid_input(only_files, exc_files, inc_files, curr_b):
    return False

  commit_files = _compute_fs(only_files, exc_files, inc_files, curr_b)

  if not commit_files:
    pprint.err('No files to commit')
    pprint.err_exp('use gl track <f> if you want to track changes to file f')
    return False

  msg = args.m if args.m else commit_dialog.show(commit_files, repo)
  if not msg.strip():
    raise ValueError('Missing commit message')

  _auto_track(commit_files, curr_b)
  ci = curr_b.create_commit(commit_files, msg)
  pprint.ok('Commit succeeded')
  if ci:
    pprint.blank()
    pprint.commit(ci)
  return True


def _valid_input(only_files, exc_files, inc_files, curr_b):
  """Validates user input.

  This function will print to stderr in case user-provided values are invalid
  (and return False).

  Args:
    only_files: user-provided list of filenames to be committed only.
    exc_files: list of filenames to be excluded from commit.
    inc_files: list of filenames to be included to the commit.

  Returns:
    True if the input is valid, False if otherwise.
  """
  if only_files and (exc_files or inc_files):
    pprint.err(
        'You provided a list of filenames to be committed only but also '
        'provided a list of files to be excluded or included')
    return False

  ret = True
  err = []
  for fp in only_files:
    try:
      f = curr_b.status_file(fp)
    except KeyError:
      err.append('File {0} doesn\'t exist'.format(fp))
      ret = False
    else:
      if f.type == core.GL_STATUS_TRACKED and not f.modified:
        err.append(
            'File {0} is a tracked file but has no modifications'.format(fp))
        ret = False

  for fp in exc_files:
    try:
      f = curr_b.status_file(fp)
    except KeyError:
      err.append('File {0} doesn\'t exist'.format(fp))
      ret = False
    else:  # Check that the files to be excluded are existing tracked files
      if f.type != core.GL_STATUS_TRACKED:
        err.append(
            'File {0}, listed to be excluded from commit, is not a tracked '
            'file'.format(fp))
        ret = False
      elif f.type == core.GL_STATUS_TRACKED and not f.modified:
        err.append(
            'File {0}, listed to be excluded from commit, is a tracked file '
            'but has no modifications'.format(fp))
        ret = False

  for fp in inc_files:
    try:
      f = curr_b.status_file(fp)
    except KeyError:
      err.append('File {0} doesn\'t exist'.format(fp))
      ret = False
    else:  # Check that the files to be included are existing untracked files
      if f.type != core.GL_STATUS_UNTRACKED:
        err.append(
            'File {0}, listed to be included in the commit, is not a untracked '
            'file'.format(fp))
        ret = False

  if not ret:  # Some error occured
    for e in err:
      pprint.err(e)

  return ret


def _compute_fs(only_files, exc_files, inc_files, curr_b):
  """Compute the final fileset to commit.

  Args:
    only_files: list of filenames to be committed only.
    exc_files: list of filenames to be excluded from commit.
    inc_files: list of filenames to be included to the commit.

  Returns:
    A list of filenames to be committed.
  """
  if only_files:
    ret = only_files
  else:
    # Tracked modified files.
    ret = frozenset(
        f.fp for f in curr_b.status()
        if f.type == core.GL_STATUS_TRACKED and f.modified)
    ret = ret.difference(exc_files)
    ret = ret.union(inc_files)

  return ret


def _auto_track(files, curr_b):
  """Tracks those untracked files in the list."""
  for fp in files:
    f = curr_b.status_file(fp)
    if f.type == core.GL_STATUS_UNTRACKED:
      curr_b.track_file(f.fp)
