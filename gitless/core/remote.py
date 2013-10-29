# Gitless - a version control system built on top of Git.
# Copyright (c) 2013  Santiago Perez De Rosso.
# Licensed under GNU GPL, version 2.

"""Gitless's remote lib."""


from gitpylib import remote as git_remote


# Ret codes of methods.
SUCCESS = 1
REMOTE_NOT_FOUND = 2
REMOTE_ALREADY_SET = 3
REMOTE_NOT_FOUND = 4
REMOTE_UNREACHABLE = 5


def add(remote_name, remote_url):
  """Add a remote for the current Gitless repo.

  Args:
    remote_name: the name of the remote.
    remote_url: the url of the remote

  Returns:
    a pair (status, out) where status is one of REMOTE_ALREADY_SET,
    REMOTE_UNREACHABLE or SUCCESS and out has additional information about the
    remote if status=SUCCESS.
  """
  if is_set(remote_name):
    return (REMOTE_ALREADY_SET, None)
  git_remote.add(remote_name, remote_url)
  ret, out = info(remote_name)
  if ret == REMOTE_UNREACHABLE:
    git_remote.rm(remote_name)
    return (REMOTE_UNREACHABLE, None)
  return (SUCCESS, out)


def is_set(remote_name):
  return remote_name in git_remote.list()


def info(remote_name):
  ret, info = git_remote.show(remote_name)
  if ret == git_remote.REMOTE_NOT_FOUND:
    return (REMOTE_NOT_FOUND, None)
  elif ret == git_remote.REMOTE_UNREACHABLE:
    return (REMOTE_UNREACHABLE, None)
  elif ret == git_remote.SUCCESS:
    return (SUCCESS, info)


def list():
  return git_remote.list()


def rm(remote_name):
  if not is_set(remote_name):
    return REMOTE_NOT_FOUND
  git_remote.rm(remote_name)
  return SUCCESS
