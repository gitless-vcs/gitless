# Gitless - a version control system built on top of Git.
# Licensed under GNU GPL v2.

"""Gitless's init lib."""


import os

import pygit2
from sh import git, ErrorReturnCode

from . import branch as branch_lib
from . import repo as repo_lib

from gitless.gitpylib import remote as git_remote


class NothingToInitError(repo_lib.GlError):

  def __init__(self):
    super(NothingToInitError, self).__init__(
        'You are already in a Gitless repository')


def init_from(remote_repo):
  """Clones the remote_repo into the cwd."""
  try:
    repo_lib.gl_dir()
    raise NothingToInitError()
  except repo_lib.NotInRepoError:
    # Expected
    try:
      git.clone(remote_repo, os.getcwd())
    except ErrorReturnCode as e:
      raise repo_lib.GlError(e.stderr)

    repo = pygit2.Repository(repo_lib.gl_dir())
    # We get all remote branches as well and create local equivalents.
    for rb_name in git_remote.branches('origin'):
      if rb_name == 'master':
        continue
      rb = repo.lookup_branch(
          'origin/{0}'.format(rb_name), pygit2.GIT_BRANCH_REMOTE)
      new_b = repo.create_branch(rb_name, rb.peel(pygit2.Commit))
      new_b.upstream = rb


def init_cwd():
  """Makes the cwd a Gitless's repository."""
  try:
    repo_lib.gl_dir()
    raise NothingToInitError()
  except repo_lib.NotInRepoError:
    # Expected
    pygit2.init_repository(os.getcwd())
