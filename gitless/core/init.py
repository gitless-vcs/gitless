# Gitless - a version control system built on top of Git.
# Copyright (c) 2013  Santiago Perez De Rosso.
# Licensed under GNU GPL, version 2.

"""Gitless's init lib."""


from . import branch as branch_lib
from . import repo as repo_lib

from gitpylib import repo as git_repo
from gitpylib import remote as git_remote


# Ret codes of methods.
SUCCESS = 1
NOTHING_TO_INIT = 2
REPO_UNREACHABLE = 3


def init_from(remote_repo):
  """Clones the remote_repo into the cwd."""
  if repo_lib.gl_dir():
    return NOTHING_TO_INIT
  if not git_repo.clone(remote_repo):
    return REPO_UNREACHABLE
  # We get all remote branches as well and create local equivalents.
  for remote_branch in git_remote.branches('origin'):
    if remote_branch == 'master':
      continue
    s = branch_lib.create(remote_branch, 'origin/{0}'.format(remote_branch))
    if s != SUCCESS:
      raise Exception(
          'Unexpected status code {0} when creating local branch {1}'.format(
              s, remote_branch))
  return SUCCESS


def init_cwd():
  """Makes the cwd a Gitless's repository."""
  if repo_lib.gl_dir():
    return NOTHING_TO_INIT
  git_repo.init()
  return SUCCESS
