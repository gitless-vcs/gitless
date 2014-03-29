# Gitless - a version control system built on top of Git.
# Licensed under GNU GPL v2.

"""Gitless's sync lib."""


import itertools
import os

from gitpylib import apply as git_apply
from gitpylib import file as git_file
from gitpylib import hook as git_hook
from gitpylib import status as git_status
from gitpylib import sync as git_sync
from gitpylib import remote as git_remote

from . import branch as branch_lib
from . import file as file_lib
from . import remote as remote_lib
from . import repo as repo_lib


# Ret codes of methods.
SUCCESS = 1
LOCAL_CHANGES_WOULD_BE_LOST = 2
SRC_NOT_FOUND = 3
SRC_IS_CURRENT_BRANCH = 4
NOTHING_TO_MERGE = 5
FILE_NOT_FOUND = 6
MERGE_NOT_IN_PROGRESS = 8
CONFLICT = 9
REBASE_NOT_IN_PROGRESS = 10
NOTHING_TO_REBASE = 11
UPSTREAM_NOT_SET = 12
NOTHING_TO_PUSH = 13
REMOTE_NOT_FOUND = 14
REMOTE_UNREACHABLE = 15
REMOTE_BRANCH_NOT_FOUND = 16
PUSH_FAIL = 17
UNRESOLVED_CONFLICTS = 19
RESOLVED_FILES_NOT_IN_COMMIT = 20
PRE_COMMIT_FAILED = 21


def merge(src):
  """Merges changes in the src branch into the current branch.

  Args:
    src: the source branch to pick up changes from.
  """
  is_remote_b = _is_remote_branch(src)
  is_valid, error = (
      _valid_remote_branch(src)
      if is_remote_b else _valid_branch(src))
  if not is_valid:
    return error, None

  if is_remote_b:
    remote, remote_b = _parse_from_remote_branch(src)
    ret, out = git_sync.pull_merge(remote, remote_b)
  else:
    ret, out = git_sync.merge(src)

  if ret == git_sync.SUCCESS:
    return SUCCESS, out
  elif ret == git_sync.CONFLICT:
    return CONFLICT, out
  elif ret == git_sync.LOCAL_CHANGES_WOULD_BE_LOST:
    return LOCAL_CHANGES_WOULD_BE_LOST, out
  elif ret == git_sync.NOTHING_TO_MERGE:
    return NOTHING_TO_MERGE, out
  raise Exception('Unexpected ret code {0}'.format(ret))


def merge_in_progress():
  return git_sync.merge_in_progress()


def abort_merge():
  if not merge_in_progress():
    return MERGE_NOT_IN_PROGRESS
  git_sync.abort_merge()
  file_lib.internal_resolved_cleanup()
  return SUCCESS


def rebase(new_base):
  is_remote_b = _is_remote_branch(new_base)
  is_valid, error = (
      _valid_remote_branch(new_base)
      if is_remote_b else _valid_branch(new_base))
  if not is_valid:
    return error, None

  current = branch_lib.current()
  if is_remote_b:
    remote, remote_b = _parse_from_remote_branch(new_base)
    ret, out = git_sync.pull_rebase(remote, remote_b)
  else:
    ret, out = git_sync.rebase(new_base)
  if ret == git_sync.SUCCESS:
    return SUCCESS, out
  elif ret == git_sync.LOCAL_CHANGES_WOULD_BE_LOST:
    return LOCAL_CHANGES_WOULD_BE_LOST, out
  elif ret == git_sync.CONFLICT:
    # We write a file to note the current branch being rebased and the new base.
    _write_rebase_file(current, new_base)
    return CONFLICT, out
  elif ret == git_sync.NOTHING_TO_REBASE:
    return NOTHING_TO_REBASE, out
  raise Exception('Unexpected ret code {0}'.format(ret))


def rebase_in_progress():
  return os.path.exists(os.path.join(repo_lib.gl_dir(), 'GL_REBASE'))


def abort_rebase():
  if not rebase_in_progress():
    return REBASE_NOT_IN_PROGRESS
  git_sync.abort_rebase()
  conclude_rebase()
  return SUCCESS


def rebase_info():
  """Gets the name of the current branch being rebased and the new base."""
  rf = open(_rebase_file(), 'r')
  current = rf.readline().strip()
  new_base = rf.readline().strip()
  return current, new_base


def skip_rebase_commit():
  if not rebase_in_progress():
    return REBASE_NOT_IN_PROGRESS
  s = git_sync.skip_rebase_commit()
  if s[0] == git_sync.SUCCESS:
    conclude_rebase()
    return SUCCESS, s[1]
  elif s[0] == git_sync.CONFLICT:
    return SUCCESS, s[1]
  else:
    raise Exception('Unexpected ret code {0}'.format(s[0]))


def conclude_rebase():
  file_lib.internal_resolved_cleanup()
  os.remove(_rebase_file())


def publish():
  """Publish local commits to the upstream branch."""
  current_b = branch_lib.current()
  b_st = branch_lib.status(current_b)
  if not b_st.upstream:
    return UPSTREAM_NOT_SET, None
  ret, out = git_sync.push(current_b, *b_st.upstream.split('/'))
  if ret == git_sync.SUCCESS:
    if not b_st.upstream_exists:
      # After the push the upstream exists. So we set it.
      branch_lib.set_upstream(b_st.upstream)
    return SUCCESS, out
  elif ret == git_sync.NOTHING_TO_PUSH:
    return NOTHING_TO_PUSH, None
  elif ret == git_sync.PUSH_FAIL:
    return PUSH_FAIL, None
  else:
    raise Exception('Unexpected ret code {0}'.format(ret))


def partial_commit(files):
  return PartialCommit(files)

class PartialCommit(object):

  def __init__(self, files):
    self.__files = files
    self.__pf = open(os.path.join(repo_lib.gl_dir(), 'GL_PARTIAL_CI'), 'w+')

  def __iter__(self):
    for fp in self.__files:
      yield self.ChunkedFile(fp, self.__pf)

  def commit(self, msg, skip_checks=False):
    def has_staged_version(fp):
      return git_status.of_file(fp) in [
          git_status.STAGED, git_status.MODIFIED_MODIFIED,
          git_status.ADDED_MODIFIED]

    self.__pf.close()
    git_apply.on_index(self.__pf.name)
    for fp in self.__files:
      if not has_staged_version(fp):
        # Partial commit includes all changes to file.
        git_file.stage(fp)
    out = git_sync.commit(
        None, msg, skip_checks=skip_checks, include_staged_files=True)
    return SUCCESS, out

  class ChunkedFile(object):

    def __init__(self, fp, pf):
      self.fp = fp
      self.__pf = pf
      self.__diff, self.__padding, _, _, self.__diff_header = git_file.diff(fp)
      if not self.__diff:
        raise Exception('There\'s nothing to (partially) commit')
      self.__diff_len = len(self.__diff)
      self.__header_printed = False
      self.__curr_index = 0
      self.__curr_chunk = None

    def __iter__(self):
      return self

    # Py 2/3 compatibility.
    def __next__(self):
      return self.next()

    def next(self):
      if self.__curr_index >= self.__diff_len:
        raise StopIteration
      self.__curr_chunk = [self.__diff[self.__curr_index]]
      self.__curr_chunk.extend(
          itertools.takewhile(
            lambda ld: ld.status != git_file.DIFF_INFO,
            itertools.islice(self.__diff, self.__curr_index + 1, None)))
      self.__curr_index += len(self.__curr_chunk)
      return self

    @property
    def diff(self):
      return self.__curr_chunk, self.__padding

    def include(self):
      if not self.__header_printed:
        self.__pf.write('\n'.join(self.__diff_header) + '\n')
      for line, _, _, _ in self.__curr_chunk:
        self.__pf.write(line + '\n')


def commit(files, msg, skip_checks=False):
  """Record changes in the local repository.

  Args:
    files: the files to commit.
    msg: the commit message.
    skip_checks: True if the pre-commit checks should be skipped (defaults to
      False).

  Returns:
    a pair (status, out) where status can be:
    - UNRESOLVED_CONFLICTS -> out is the list of unresolved files.
    - PRE_COMMIT_FAILED -> out is the output from the pre-commit hook.
    - SUCCESS -> out is the output of the commit command.
  """
  in_rebase = rebase_in_progress()
  in_merge = merge_in_progress()
  if in_rebase or in_merge:
    # If we are doing a merge then we can't do a partial commit (Git won't let
    # us do it). We can do commit -i which will stage all the files but we need
    # to watch out for not commiting new Gitless's tracked files that are not in
    # the list.
    # To do this, we temporarily unstage these files and then re-stage them
    # after the commit.
    # TODO(sperezde): actually implement what the comment above says ;)
    # TODO(sperezde): also need to do something with deletions?
    unresolved = []
    resolved = []
    for f in file_lib.status_all():
      if f.in_conflict:
        unresolved.append(f)
      elif f.resolved:
        resolved.append(f)

    if unresolved:
      return UNRESOLVED_CONFLICTS, unresolved
    # We know that there are no pending conflicts to be resolved.
    # Let's check that all resolved files are in the commit.
    resolved_not_in_ci = [f for f in resolved if f.fp not in files]
    if resolved_not_in_ci:
      return RESOLVED_FILES_NOT_IN_COMMIT, resolved_not_in_ci

    # print 'commiting files %s' % files
    out = None
    if in_rebase:
      # TODO(sperezde): save the message to use it later.
      for f in files:
        git_file.stage(f)
      file_lib.internal_resolved_cleanup()
      if not skip_checks:
        pc = git_hook.pre_commit()
        if not pc.ok:
          return PRE_COMMIT_FAILED, pc.err
      s = git_sync.rebase_continue()
      if s[0] == SUCCESS:
        conclude_rebase()
        return SUCCESS, s[1]
      elif s[0] == CONFLICT:
        # TODO(sperezde): the next apply could actually result in another
        # conflict.
        return SUCCESS, s[1]
      else:
        raise Exception('Unexpected ret code {0}'.format(s[0]))

    # It's a merge.
    if not skip_checks:
      pc = git_hook.pre_commit()
      if not pc.ok:
        return PRE_COMMIT_FAILED, pc.err
    out = git_sync.commit(
        files, msg, skip_checks=True, include_staged_files=True)
    file_lib.internal_resolved_cleanup()
    return SUCCESS, out

  # It's a regular commit.
  if not skip_checks:
    pc = git_hook.pre_commit()
    if not pc.ok:
      return PRE_COMMIT_FAILED, pc.err
  return SUCCESS, git_sync.commit(files, msg, skip_checks=True)


# Private methods.


def _write_rebase_file(current, new_base):
  with open(_rebase_file(), 'w') as rf:
    rf.write(current + '\n')
    rf.write(new_base + '\n')


def _rebase_file():
  return os.path.join(repo_lib.gl_dir(), 'GL_REBASE')


def _valid_branch(b):
  b_st = branch_lib.status(b)
  if not b_st:
    return False, SRC_NOT_FOUND
  if b_st and b_st.is_current:
    return False, SRC_IS_CURRENT_BRANCH
  return True, None


def _valid_remote_branch(b):
  remote_n, remote_b = b.split('/')
  if not remote_lib.is_set(remote_n):
    return False, REMOTE_NOT_FOUND

  # We know the remote exists, let's see if the branch exists.
  exists, err = git_remote.head_exist(remote_n, remote_b)
  if not exists:
    if err == git_remote.REMOTE_UNREACHABLE:
      ret_err = REMOTE_UNREACHABLE
    else:
      ret_err = REMOTE_BRANCH_NOT_FOUND
    return False, ret_err

  return True, None


def _is_remote_branch(b):
  return '/' in b


def _parse_from_remote_branch(b):
  return b.split('/')
