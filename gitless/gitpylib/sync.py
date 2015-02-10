# gitpylib - a Python library for Git.
# Licensed under GNU GPL v2.

"""Sync module for Git sync operations."""


import os
import re

from . import common


SUCCESS = 1
LOCAL_CHANGES_WOULD_BE_LOST = 2
NOTHING_TO_MERGE = 3
NOTHING_TO_REBASE = 4
CONFLICT = 5
NOTHING_TO_PUSH = 6
PUSH_FAIL = 7


def commit(files, msg, skip_checks=False, include_staged_files=False):
  """Record changes in the local repository.

  Args:
    files: the files to commit.
    msg: the commit message.
    skip_checks: if the pre-commit hook should be skipped or not. (Defaults to
      False.)
    include_staged_files: whether to include the contents of the staging area in
      the commit or not. (Defaults to False.)

  Returns:
    the output of the commit command.
  """
  cmd = 'commit {0}-m"{1}"'.format('--no-verify ' if skip_checks else '', msg)
  if not files and include_staged_files:
    return common.safe_git_call(cmd)[0]

  return common.safe_git_call(
      '{0} {1}-- "{2}"'.format(
          cmd, '-i ' if include_staged_files else '', '" "'.join(files)))[0]


def merge(src):
  """Merges changes in the src branch into the current branch.

  Args:
    src: the source branch to pick up changes from.
  """
  ok, out, err = common.git_call('merge {0}'.format(src))
  return _parse_merge_output(ok, out, err)


def _parse_merge_output(ok, out, err):
  if not ok:
    #if out.startswith('Auto-merging'):
      # conflict?
    #  raise Exception('conflict?')
    if ('Automatic merge failed; fix conflicts and then commit the result.'
            in out):
      return CONFLICT, None
    else:
      return LOCAL_CHANGES_WOULD_BE_LOST, err.splitlines()[1:-2]
  if out == 'Already up-to-date.\n':
    return NOTHING_TO_MERGE, None
  return SUCCESS, None


def abort_merge():
  """Aborts the current merge."""
  common.safe_git_call('merge --abort')


def merge_in_progress():
  return os.path.exists(os.path.join(common.git_dir(), 'MERGE_HEAD'))


def rebase(new_base):
  ok, out, err = common.git_call('rebase {0}'.format(new_base))
  return _parse_rebase_output(ok, out, err)


def _parse_rebase_output(ok, out, err):
  # print 'out is <%s>, err is <%s>' % (out, err)
  if not ok:
    if 'Please commit or stash them' in err:
      # TODO(sperezde): add the files whose changes would be lost.
      return LOCAL_CHANGES_WOULD_BE_LOST, None
    elif ('The following untracked working tree files would be overwritten'
          in err):
      # TODO(sperezde): add the files whose changes would be lost.
      return LOCAL_CHANGES_WOULD_BE_LOST, None
    return CONFLICT, None
  if re.match(r'Current branch [^\s]+ is up to date.\n', out):
    return NOTHING_TO_REBASE, None
  return SUCCESS, out


def rebase_continue():
  ok, out, _ = common.git_call('rebase --continue')
  # print 'out is <%s>, err is <%s>' % (out, err)
  if not ok:
    return CONFLICT, None
  return SUCCESS, out


def skip_rebase_commit():
  ok, out, _ = common.git_call('rebase --skip')
  # print 'out is <%s>, err is <%s>' % (out, err)
  if not ok:
    return CONFLICT, None
  return SUCCESS, out


def abort_rebase():
  common.safe_git_call('rebase --abort')


def rebase_in_progress():
  return os.path.exists(os.path.join(common.git_dir(), 'rebase-apply'))


def push(src_branch, dst_remote, dst_branch):
  _, _, err = common.git_call(
      'push {0} {1}:{2}'.format(dst_remote, src_branch, dst_branch))
  if err == 'Everything up-to-date\n':
    return NOTHING_TO_PUSH, None
  elif ('Updates were rejected because a pushed branch tip is behind its remote'
        in err):
    return PUSH_FAIL, None
  # Not sure why, but git push returns output in stderr.
  return SUCCESS, err


def pull_rebase(remote, remote_b):
  ok, out, err = common.git_call(
      'pull --rebase {0} {1}'.format(remote, remote_b))
  return _parse_rebase_output(ok, out, err)


def pull_merge(remote, remote_b):
  ok, out, err = common.git_call('pull {0} {1}'.format(remote, remote_b))
  return _parse_merge_output(ok, out, err)
