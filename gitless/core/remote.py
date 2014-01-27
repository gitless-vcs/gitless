# Gitless - a version control system built on top of Git.
# Copyright (c) 2013  Santiago Perez De Rosso.
# Licensed under GNU GPL, version 2.

"""Gitless's remote lib."""


import collections

from gitpylib import remote as git_remote


# Ret codes of functions.
SUCCESS = 1
REMOTE_NOT_FOUND = 2
REMOTE_ALREADY_SET = 3
REMOTE_NOT_FOUND = 4
REMOTE_UNREACHABLE = 5
INVALID_NAME = 6


def add(remote_name, remote_url):
  """Add a remote.

  Args:
    remote_name: the name of the remote.
    remote_url: the url of the remote

  Returns:
    REMOTE_ALREADY_SET, REMOTE_UNREACHABLE or SUCCESS.
  """
  if '/' in remote_name:
    return INVALID_NAME
  if __is_set(remote_name):
    return REMOTE_ALREADY_SET
  s = git_remote.add(remote_name, remote_url)
  if s == git_remote.REMOTE_UNREACHABLE:
    return REMOTE_UNREACHABLE
  elif s == git_remote.SUCCESS:
    return SUCCESS
  else:
    raise Exception('Unrecognized ret code {0}'.format(s))


def info(remote_name):
  ret, info = git_remote.show(remote_name)
  if ret == git_remote.REMOTE_NOT_FOUND:
    return (REMOTE_NOT_FOUND, None)
  elif ret == git_remote.REMOTE_UNREACHABLE:
    return (REMOTE_UNREACHABLE, None)
  elif ret == git_remote.SUCCESS:
    return (SUCCESS, info)


RemoteInfo = collections.namedtuple(
    'RemoteInfo', ['name', 'downstream', 'upstream'])


def info_all():
  for ri in git_remote.show_all_v():
    yield RemoteInfo(ri.name, ri.fetch, ri.push)


def rm(remote_name):
  if not __is_set(remote_name):
    return REMOTE_NOT_FOUND
  git_remote.rm(remote_name)
  return SUCCESS


# Private functions.


def __is_set(remote_name):
  return remote_name in git_remote.show_all()
