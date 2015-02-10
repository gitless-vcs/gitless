# gitpylib - a Python library for Git.
# Licensed under GNU GPL v2.

"""Module for dealing with Git remotes."""


import collections
import re

from . import common


SUCCESS = 1
REMOTE_NOT_FOUND = 2
REMOTE_UNREACHABLE = 3
REMOTE_BRANCH_NOT_FOUND = 4


def add(remote_name, remote_url):
  """Adds the given remote.

  Adds the remote mapping and also does a fetch.

  Args:
    remote_name: the name of the remote to add.
    remote_url: the url of the remote to add.

  Returns:
    SUCCESS or REMOTE_UNREACHABLE.
  """
  if _show(remote_url)[0] == REMOTE_UNREACHABLE:
    return REMOTE_UNREACHABLE
  common.safe_git_call('remote add {0} {1}'.format(remote_name, remote_url))
  common.safe_git_call('fetch {0}'.format(remote_name))
  return SUCCESS


def show(remote_name):
  """Get information about the given remote.

  Args:
    remote_name: the name of the remote to get info from.

  Returns:
    a tuple (status, out) where status is one of SUCCESS, REMOTE_NOT_FOUND, or
    REMOTE_UNREACHABLE and out is the output of the show command on success.
  """
  if remote_name not in show_all():
    return REMOTE_NOT_FOUND, None
  return _show(remote_name)


def show_all():
  """Get information of all the remotes."""
  out, _ = common.safe_git_call('remote')
  return out.splitlines()


RemoteInfo = collections.namedtuple(
    'RemoteInfo', ['name', 'fetch', 'push'])


def show_all_v():
  """Get information of all the remotes (verbose)."""
  out, _ = common.safe_git_call('remote -v')
  # format is remote_name  url (fetch/push)
  pattern = r'(\w+)\s+(.+)\s+\((\w+)\)'
  ret = {}
  for r in out.splitlines():
    result = re.match(pattern, r)
    if not result:
      raise common.UnexpectedOutputError('remote', r)
    remote_name = result.group(1)
    url = result.group(2)
    url_type = result.group(3)
    if remote_name not in ret:
      ret[remote_name] = {}
    ret[remote_name][url_type] = url
  return [
      RemoteInfo(rn, ret[rn]['fetch'], ret[rn]['push']) for rn in ret.keys()]


def rm(remote_name):
  common.safe_git_call('remote rm {0}'.format(remote_name))


def head_exist(remote_name, head):
  ok, out, _ = common.git_call(
      'ls-remote --heads {0} {1}'.format(remote_name, head))
  if not ok:
    return False, REMOTE_UNREACHABLE
  return len(out) > 0, REMOTE_BRANCH_NOT_FOUND


def branches(remote_name):
  """Gets the name of the branches in the given remote."""
  out, _ = common.safe_git_call('branch -r')
  remote_name_len = len(remote_name)
  for line in out.splitlines():
    if '->' in line:
      continue
    line = line.strip()
    if line.startswith(remote_name):
      yield line[remote_name_len+1:]


# Private functions.


def _show(remote):
  ok, out, err = common.git_call('remote show {0}'.format(remote))
  if not ok:
    if 'fatal: Could not read from remote repository' in err:
      return REMOTE_UNREACHABLE, None
    raise common.UnexpectedOutputError('remote', out, err=err)
  return SUCCESS, out
