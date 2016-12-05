# -*- coding: utf-8 -*-
# Gitless - a version control system built on top of Git.
# Licensed under GNU GPL v2.

"""gl commit - Record changes in the local repository."""


from __future__ import unicode_literals

import subprocess

import sys
if sys.platform != 'win32':
  from sh import git
else:
  from pbs import Command
  git = Command('git')

from gitless import core

from . import commit_dialog
from . import helpers, pprint


def parser(subparsers, repo):
  """Adds the commit parser to the given subparsers object."""
  desc = 'save changes to the local repository'
  commit_parser = subparsers.add_parser(
      'commit', help=desc, description=(
        desc.capitalize() + '. ' +
        'By default all tracked modified files are committed. To customize the'
        ' set of files to be committed use the only, exclude, and include '
        'flags'))
  commit_parser.add_argument(
      '-m', '--message', help='Commit message', dest='m')
  commit_parser.add_argument(
      '-p', '--partial',
      help='Interactively select segments of files to commit', dest='p',
      action='store_true')
  helpers.oei_flags(commit_parser, repo)
  commit_parser.set_defaults(func=main)


def main(args, repo):
  commit_files = helpers.oei_fs(args, repo)

  if not commit_files:
    pprint.err('No files to commit')
    pprint.err_exp('use gl track f if you want to track changes to file f')
    return False

  curr_b = repo.current_branch
  partials = None
  if args.p:
    partials = _do_partial_selection(commit_files, curr_b)

  if not repo.config['user.name']:
    pprint.err('Missing name for commit author')
    pprint.err_exp('change the value of git\'s user.name setting')
    return False
  if not repo.config['user.email']:
    pprint.err('Missing email for commit author')
    pprint.err_exp('change the value of git\'s user.email setting')
    return False

  msg = args.m if args.m else commit_dialog.show(commit_files, repo)
  if not msg.strip():
    if partials:
      git.reset('HEAD', partials)
    raise ValueError('Missing commit message')

  _auto_track(commit_files, curr_b)
  ci = curr_b.create_commit(commit_files, msg, partials=partials)
  pprint.ok('Commit succeeded')

  pprint.blank()
  pprint.commit(ci)

  if curr_b.fuse_in_progress:
    _op_continue(curr_b.fuse_continue, 'Fuse')
  elif curr_b.merge_in_progress:
    _op_continue(curr_b.merge_continue, 'Merge')

  return True


def _do_partial_selection(files, curr_b):
  partials = []
  for fp in files:
    f_st = curr_b.status_file(fp)
    if not f_st.exists_at_head:
      pprint.warn('Can\'t select segments for new file {0}'.format(fp))
      continue
    if not f_st.exists_in_wd:
      pprint.warn('Can\'t select segments for deleted file {0}'.format(fp))
      continue

    subprocess.call(['git', 'add', '-p', fp])
    # TODO: check that at least one hunk was staged
    partials.append(fp)

  return partials


def _auto_track(files, curr_b):
  """Tracks those untracked files in the list."""
  for fp in files:
    f = curr_b.status_file(fp)
    if f.type == core.GL_STATUS_UNTRACKED:
      curr_b.track_file(f.fp)


def _op_continue(op, fn):
  pprint.blank()
  try:
    op(op_cb=pprint.OP_CB)
    pprint.ok('{0} succeeded'.format(fn))
  except core.ApplyFailedError as e:
    pprint.ok('{0} succeeded'.format(fn))
    raise e
