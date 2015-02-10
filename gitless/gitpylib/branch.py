# gitpylib - a Python library for Git.
# Licensed under GNU GPL v2.

"""Module for dealing with Git branches."""


import collections
import re

from . import common


BranchStatus = collections.namedtuple(
  'BranchStatus', ['name', 'is_current', 'tracks'])

SUCCESS = 1
UNFETCHED_OBJECT = 2
INVALID_NAME = 3
NONEXISTENT_BRANCH = 4
BRANCH_ALREADY_EXISTS = 5
INVALID_SP = 6


def checkout(name):
  """Checkout branch.

  Args:
    name: the name of the branch to checkout.

  Returns:
    SUCCESS or NONEXISTENT_BRANCH
  """
  ok, _, _ = common.git_call('checkout {0}'.format(name))
  if not ok:
    return NONEXISTENT_BRANCH
  return SUCCESS


def create(name, sp='HEAD'):
  """Creates a new branch with the given name.

  Args:
    name: the name of the branch to create.
    sp: starting point. The commit from where to 'branch out.' (Defaults to
      HEAD.)

  Returns:
    SUCCESS, INVALID_NAME or BRANCH_ALREADY_EXISTS.
  """
  ok, _, err = common.git_call('branch {0} {1}'.format(name, sp))
  if not ok:
    if 'is not a valid branch name' in err:
      return INVALID_NAME
    elif 'already exists' in err:
      return BRANCH_ALREADY_EXISTS
    elif 'Not a valid object name' in err:
      return INVALID_SP
  return SUCCESS


def force_delete(name):
  """Force-deletes the branch with the given name.

  Args:
    name: the name of the branch to delete.

  Returns:
    SUCCESS or NONEXISTENT_BRANCH
  """
  ok, _, _ = common.git_call('branch -D {0}'.format(name))
  if not ok:
    return NONEXISTENT_BRANCH
  return SUCCESS


def current():
  """Get the name of the current branch."""
  for name, is_current, _ in status_all():
    if is_current:
      return name


def status(name):
  """Get the status of the branch with the given name.

  Args:
    name: the name of the branch to status.

  Returns:
    None if the branch doesn't exist or a namedtuple (name, is_current, tracks)
    where is_current is a boolean value and tracks is a string representing the
    remote branch it tracks (in the format 'remote_name/remote_branch') or None
    if it is a local branch.
  """
  out, _ = common.safe_git_call('branch --list -vv {0}'.format(name))
  if not out:
    return None

  return _parse_output(out)


def status_all():
  """Get the status of all existing branches.

  Yields:
    namedtuples of the form (name, is_current, tracks) where is_current is a
    boolean value and tracks is a string representing the remote branch it
    tracks (in the format 'remote_name/remote_branch') or None if it is a local
    branch. name could be equal to '(no branch)' if the user is in no branch.
  """
  out, _ = common.safe_git_call('branch --list -vv')
  for b in out.splitlines():
    yield _parse_output(b)


def set_upstream(branch, upstream_branch):
  """Sets the upstream branch to branch.

  Args:
    branch: the branch to set an upstream branch.
    upstream_branch: the upstream branch.
  """
  ok, _, _ = common.git_call(
      'branch --set-upstream {0} {1}'.format(branch, upstream_branch))

  if not ok:
    return UNFETCHED_OBJECT

  return SUCCESS


def unset_upstream(branch):
  """Unsets the upstream branch to branch.

  Args:
    branch: the branch to unset its upstream.
  """
  common.git_call('branch --unset-upstream {0}'.format(branch))
  return SUCCESS


def _parse_output(out):
  """Parses branch list output.

  Args:
    out: the output for one branch.

  Returns:
    a tuple (name, is_current, tracks) where is_current is a boolean value and
    tracks is a string representing the remote branch it tracks (in
    the format 'remote_name/remote_branch') or None if it is a local branch.
  """
  # * indicates whether it's the current branch or not, next comes the name of
  # the branch followed by the sha1, optionally followed by some remote tracking
  # info (between brackets) and finally the message of the last commit.
  if out.startswith('* (no branch)'):
    return BranchStatus('(no branch)', True, None)

  pattern = r'([\*| ]) ([^\s]+)[ ]+\w+ (.+)'
  result = re.match(pattern, out)
  if not result:
    raise common.UnexpectedOutputError('branch', out)

  tracks = None
  if result.group(3)[0] == '[':
    track_info = result.group(3).split(']')[0][1:]
    tracks = ''
    if ':' in track_info:
      tracks = track_info.split(':')[0]
    else:
      tracks = track_info
  return BranchStatus(result.group(2), result.group(1) == '*', tracks)
