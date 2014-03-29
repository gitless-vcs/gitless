# Gitless - a version control system built on top of Git.
# Licensed under GNU GPL v2.

"""gl commit - Record changes in the local repository."""


from gitless.core import file as file_lib
from gitless.core import sync as sync_lib

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
      '-p', '--partial', help='do a partial commit', action='store_true')
  commit_parser.add_argument(
      '-sc', '--skip-checks', help='skip pre-commit check', action='store_true',
      default=False, dest='sc')
  commit_parser.add_argument(
      '-m', '--message', help='Commit message', dest='m')
  commit_parser.set_defaults(func=main)


def main(args):
  # TODO(sperezde): re-think this worflow a bit.

  only_files = frozenset(args.only_files)
  exc_files = frozenset(args.exc_files) if args.exc_files else []
  inc_files = frozenset(args.inc_files) if args.inc_files else []

  if not _valid_input(only_files, exc_files, inc_files):
    return False

  commit_files = _compute_fs(only_files, exc_files, inc_files)

  if not commit_files:
    pprint.err('Commit aborted')
    pprint.err('No files to commit')
    pprint.err_exp('use gl track <f> if you want to track changes to file f')
    return False

  msg = args.m
  if not msg:
    # Show the commit dialog.
    msg, commit_files = commit_dialog.show(commit_files)
    if not msg.strip() and not sync_lib.rebase_in_progress():
      pprint.err('Commit aborted')
      pprint.err('No commit message provided')
      return False
    if not commit_files:
      pprint.err('Commit aborted')
      pprint.err('No files to commit')
      pprint.err_exp('use gl track <f> if you want to track changes to file f')
      return False
    if not _valid_input(commit_files, [], []):
      return False

  _auto_track(commit_files)
  commit = sync_lib.commit if not args.partial else _do_partial_commit
  ret, out = commit(commit_files, msg, skip_checks=args.sc)
  if not ret:
    pprint.msg('Commit aborted')
    return True
  if ret == sync_lib.SUCCESS:
    if out:
      pprint.msg(out)
  elif ret == sync_lib.PRE_COMMIT_FAILED:
    pprint.err('Commit aborted')
    pprint.err('The pre-commit check failed:')
    pprint.err_exp('fix the problems and run gl commit again')
    pprint.err_exp(
        'alternatively, you can skip the pre-commit checks with the '
        '--skip-checks flag')
    pprint.err_blank()
    pprint.err(out)
  elif ret == sync_lib.UNRESOLVED_CONFLICTS:
    pprint.err('Commit aborted')
    pprint.err('You have unresolved conflicts:')
    pprint.err_exp(
        'use gl resolve <f> to mark file f as resolved once you fixed the '
        'conflicts')
    for f in out:
      pprint.err_item(f.fp)
    return False
  elif ret == sync_lib.RESOLVED_FILES_NOT_IN_COMMIT:
    pprint.err('Commit aborted')
    pprint.err('You have resolved files that were not included in the commit:')
    pprint.err_exp('these must be part of the commit')
    for f in out:
      pprint.err_item(f.fp)
    return False
  else:
    raise Exception('Unexpected return code {0}'.format(ret))

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
        f.fp for f in file_lib.status_all() if f.type == file_lib.TRACKED and
        f.modified)
    # TODO(sperezde): the following is a mega-hack, do it right.
    from gitpylib import common
    ret = ret.difference(common.real_case(exc_f) for exc_f in exc_files)
    ret = ret.union(common.real_case(inc_f) for inc_f in inc_files)

  return ret


def _auto_track(files):
  """Tracks those untracked files in the list."""
  for fp in files:
    f = file_lib.status(fp)
    if not f:
      raise Exception('Expected {0} to exist, but it doesn\'t'.format(fp))
    if f.type == file_lib.UNTRACKED:
      file_lib.track(f.fp)


def _do_partial_commit(files, msg, skip_checks=False):
  pprint.msg('Entering partial commit mode')
  pprint.exp(
      'you can always input "a" or "abort" or "q" or "quit" to abort the '
      'commit')
  pc = sync_lib.partial_commit(files)
  for chunked_fp in pc:
    print('\n')
    pprint.msg('Looking at file "{0}"'.format(chunked_fp.fp))
    for chunk in chunked_fp:
      while True:
        pprint.diff(*chunk.diff)
        print('\n')
        pprint.msg('Do you want to include this chunk in the commit?')
        pprint.exp('input "y" or "yes" to include this chunk in the commit')
        pprint.exp('input "n" or "no" to leave this chunk out of the commit')
        pprint.exp(
            'input "a" or "abort" or "q" or "quit" to abort the commit')
        user_input = pprint.get_user_input()
        if user_input in ['y', 'yes']:
          chunk.include()
          break
        elif user_input in ['n', 'no']:
          break
        elif user_input in ['a', 'abort', 'q', 'quit']:
          return None, None
        else:
          pprint.msg(
              'Unrecognized input "{0}", please try again'.format(user_input))
  return pc.commit(msg, skip_checks=skip_checks)
