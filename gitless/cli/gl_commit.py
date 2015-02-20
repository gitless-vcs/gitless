# Gitless - a version control system built on top of Git.
# Licensed under GNU GPL v2.

"""gl commit - Record changes in the local repository."""


from gitless.core import file as file_lib
from gitless.core import core

from . import commit_dialog
from . import pprint


def parser(subparsers):
  """Adds the commit parser to the given subparsers object."""
  commit_parser = subparsers.add_parser(
      'commit', help='record changes in the local repository')
  commit_parser.add_argument(
      'only_files', nargs='*',
      help='only the files listed as arguments will be committed (files could '
           'be tracked or untracked files)')
  commit_parser.add_argument(
      '-exc', '--exclude', nargs='+',
      help=('files listed as arguments will be excluded from the commit (files '
            'must be tracked files)'),
      dest='exc_files')
  commit_parser.add_argument(
      '-inc', '--include', nargs='+',
      help=('files listed as arguments will be included to the commit (files '
            'must be untracked files)'),
      dest='inc_files')
  commit_parser.add_argument(
      '-m', '--message', help='Commit message', dest='m')
  commit_parser.set_defaults(func=main)


def main(args):
  only_files = frozenset(args.only_files)
  exc_files = frozenset(args.exc_files if args.exc_files else [])
  inc_files = frozenset(args.inc_files if args.inc_files else [])


  if not _valid_input(only_files, exc_files, inc_files):
    return False

  commit_files = _compute_fs(only_files, exc_files, inc_files)

  if not commit_files:
    pprint.err('Commit aborted')
    pprint.err('No files to commit')
    pprint.err_exp('use gl track <f> if you want to track changes to file f')
    return False

  repo = core.Repository()
  msg = args.m if args.m else commit_dialog.show(commit_files, repo)
  if not msg.strip():
    raise ValueError('Missing commit message')

  _auto_track(commit_files)
  repo.current_branch.create_commit(commit_files, msg)
  pprint.msg('Commit succeeded')
  return True


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
    pprint.err('Commit aborted')
    pprint.err(
        'You provided a list of filenames to be committed only but also '
        'provided a list of files to be excluded or included.')
    return False

  ret = True
  err = []
  for fp in only_files:
    f = file_lib.status(fp)
    if not f:
      err.append('File {0} doesn\'t exist'.format(fp))
      ret = False
    elif f.type == file_lib.TRACKED and not f.modified:
      err.append(
          'File {0} is a tracked file but has no modifications'.format(fp))
      ret = False

  for fp in exc_files:
    f = file_lib.status(fp)
    # We check that the files to be excluded are existing tracked files.
    if not f:
      err.append('File {0} doesn\'t exist'.format(fp))
      ret = False
    elif f.type != file_lib.TRACKED:
      err.append(
          'File {0}, listed to be excluded from commit, is not a tracked '
          'file'.format(fp))
      ret = False
    elif f.type == file_lib.TRACKED and not f.modified:
      err.append(
          'File {0}, listed to be excluded from commit, is a tracked file but '
          'has no modifications'.format(fp))
      ret = False
    elif f.resolved:
      err.append('You can\'t exclude a file that has been resolved')
      ret = False

  for fp in inc_files:
    f = file_lib.status(fp)
    # We check that the files to be included are existing untracked files.
    if not f:
      err.append('File {0} doesn\'t exist'.format(fp))
      ret = False
    elif f.type != file_lib.UNTRACKED:
      err.append(
          'File {0}, listed to be included in the commit, is not a untracked '
          'file'.format(fp))
      ret = False

  if not ret:
    # Some error occured.
    pprint.err('Commit aborted')
    for e in err:
      pprint.err(e)

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
  if only_files:
    ret = only_files
  else:
    # Tracked modified files.
    ret = frozenset(
        f.fp for f in file_lib.status_all(relative_paths=True)
          if f.type == file_lib.TRACKED and f.modified)
    ret = ret.difference(exc_files)
    ret = ret.union(inc_files)

  return ret


def _auto_track(files):
  """Tracks those untracked files in the list."""
  for fp in files:
    f = file_lib.status(fp)
    if not f:
      raise Exception('Expected {0} to exist, but it doesn\'t'.format(fp))
    if f.type == file_lib.UNTRACKED:
      file_lib.track(f.fp)
