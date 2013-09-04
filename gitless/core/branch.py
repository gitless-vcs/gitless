# Gitless - a version control system built on top of Git.
# Copyright (c) 2013  Santiago Perez De Rosso.
# Licensed under GNU GPL, version 2.

"""Gitless's branching lib."""


import os
import re
import shutil

from gitpylib import branch as git_branch
from gitpylib import common as git_common
from gitpylib import file as git_file
from gitpylib import stash as git_stash
from gitpylib import status as git_status

import sync as sync_lib
import remote as remote_lib
import repo as repo_lib


SUCCESS = 1
REMOTE_NOT_FOUND = 2
INVALID_NAME = 3


def create(name):
  """Creates a new branch with the given name.

  Args:
    name: the name of the branch to create.

  Returns:
    INVALID_NAME if the name is invalid or SUCCESS if the branch was created
    successfully.
  """
  if '/' in name or '_' in name:
    # Branches can't have a '/' so that we don't confuse them with remote
    # branches that can be specified in the form remote/branch.
    # Also, they can't have a '_' so that it doesn't conflict with our way of
    # naming internal files.
    return INVALID_NAME
  ret = git_branch.create(name)
  if ret is git_branch.INVALID_NAME:
    return INVALID_NAME
  elif ret is git_branch.SUCCESS:
    return SUCCESS
  else:
    raise Exception('Unrecognized ret code %s' % ret)


def delete(name):
  """Deletes the branch with the given name.

  Args:
    name: the name of the branch to delete.
  """
  git_branch.force_delete(name)
  # We also cleanup any stash left.
  git_stash.drop(_stash_msg(name))


def set_upstream(upstream_remote, upstream_branch):
  """Sets the upstream branch of the current branch.

  Args:
    upstream_remote: the upstream remote.
    upstream_branch: the upstream branch.

  Returns:
    REMOTE_NOT_FOUND if the remote hasn't been defined yet or SUCCESS if the
    operation finished successfully.
  """
  if not remote_lib.is_set(upstream_remote):
    return REMOTE_NOT_FOUND

  ub = '/'.join([upstream_remote, upstream_branch])

  current_b = current()
  ret = git_branch.set_upstream(current_b, ub)
  uf = _upstream_file(current_b, upstream_remote, upstream_branch)
  if os.path.exists(uf):
    os.remove(uf)
  if ret is git_branch.UNFETCHED_OBJECT:
    # We work around this, it could be the case that the user is trying to push
    # a new branch to the remote or it could be that the branch exists but it
    # hasn't been fetched yet.
    # TODO(sperezde): fix the fetch case.
    open(uf, 'a').close()
  return SUCCESS


def detach(name):
  """Detaches the branch with the given name from its remote.

  Args:
    name: the name of the branch to detach.
  """
  # TBD


def switch(name):
  """Switches to the branch with the given name.

  Args:
    name: the name of the destination branch.
  """
  current_b = current()
  # Stash doesn't save assumed unchanged files, so we save which files are
  # marked as assumed unchanged and unmark them. And when switching back we
  # look at this info and re-mark them.
  _unmark_au_files(current_b)
  git_stash.all(_stash_msg(current_b))
  git_branch.checkout(name)
  git_stash.pop(_stash_msg(name))
  _remark_au_files(name)


def status(name):
  """Get the status of the branch with the given name.

  Args:
    name: the name of the branch to status.

  Returns:
    A tuple (exists, is_current, tracks) where exists and is_current are boolean
    values and tracks is a string representing the remote branch it tracks (in
    the format 'remote_name/remote_branch') or None if it is a local branch.
  """
  return git_branch.status(name)


def current():
  """Get the name of the current branch."""
  if sync_lib.rebase_in_progress():
    # While in a rebase, Git actually moves to a "no-branch" status.
    # In Gitless, the user is in the branch being re-based.
    return sync_lib.rebase_info()[0]
  return git_branch.current()


def status_all():
  """Get the status of all existing branches.

  Returns:
    Tuples of the form (name, is_current, upstream, upstream_in_remote).
    upstream is in the format 'remote_name/remote_branch'.
  """
  rebase_in_progress = sync_lib.rebase_in_progress()
  if rebase_in_progress:
    current = sync_lib.rebase_info()[0]

  ret = []
  for name, is_current, tracks in git_branch.status_all():
    if name == '(no branch)':
      continue

    new_current = is_current
    new_tracks = tracks
    upstream_in_remote = True
    if rebase_in_progress and name == current:
        new_current = True
    if not tracks:
      # We check if the branch has an unpushed upstream
      ur, ub = upstream(name)
      if ur:
        new_tracks = '/'.join([ur, ub])
        upstream_in_remote = False

    ret.append((name, new_current, new_tracks, upstream_in_remote))

  return ret


def has_unpushed_upstream(branch, upstream_remote, upstream_branch):
  """True if branch has upstream_remote/upstream_branch set but unpushed."""
  return os.path.exists(
      _upstream_file(branch, upstream_remote, upstream_branch))


def upstream(branch):
  """Gets the upstream branch of the given branch.

  Args:
    branch: the branch whose upstream will be returned.

  Returns:
    a pair (upstream_remote, upstream_branch) or None if the given branch has no
    upstream set.
  """
  exists, is_current, tracks = status(branch)
  if tracks:
    return tracks.split('/')
  for f in os.listdir(repo_lib.gl_dir()):
    result = re.match('GL_UPSTREAM_%s_(\w+)_(\w+)' % branch, f)
    if result:
      return (result.group(1), result.group(2))
  return (None, None)


# Private methods.


def _stash_msg(name):
  """Computes the stash msg to use for stashing changes in branch name."""
  return '---gl-%s---' % name


def _upstream_file(branch, upstream_remote, upstream_branch):
  upstream_fn = 'GL_UPSTREAM_%s_%s_%s' % (
      branch, upstream_remote, upstream_branch)
  return os.path.join(repo_lib.gl_dir(), upstream_fn)


def _unmark_au_files(branch):
  """Saves the path of files marked as assumed unchanged and unmarks them.

  To re-mark all files again use _remark_au_files(branch).

  Args:
    branch: the info will be stored under this branch name.
  """
  assumed_unchanged_fps = git_status.au_files()
  if not assumed_unchanged_fps:
    return

  gl_dir = repo_lib.gl_dir()
  f = open(os.path.join(gl_dir, 'GL_AU_%s' % branch), 'w')

  repo_dir = git_common.repo_dir()
  for fp in assumed_unchanged_fps:
    f.write(fp + '\n')
    git_file.not_assume_unchanged(os.path.join(repo_dir, fp))


def _remark_au_files(branch):
  """Re-marks files as assumed unchanged.

  Args:
    branch: the branch name under which the info is stored.
  """
  gl_dir = repo_lib.gl_dir()
  au_info_fp = os.path.join(gl_dir, 'GL_AU_%s' % branch)
  if not os.path.exists(au_info_fp):
    return

  f = open(au_info_fp, 'r')

  repo_dir = git_common.repo_dir()
  for fp in f:
    fp = fp.strip()
    git_file.assume_unchanged(os.path.join(repo_dir, fp))

  os.remove(au_info_fp)
