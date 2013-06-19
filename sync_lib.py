"""Gitless's sync lib."""


import os

from gitpylib import file
from gitpylib import status
from gitpylib import sync
import branch_lib
import lib


SUCCESS = 1
LOCAL_CHANGES_WOULD_BE_LOST = 2
SRC_NOT_FOUND = 3
SRC_IS_CURRENT_BRANCH = 4
NOTHING_TO_MERGE = 5
FILE_NOT_FOUND = 6
FILE_NOT_IN_CONFLICT = 7


def merge(src):
  """Merges changes in the src branch into the current branch.

  Args:
    src: the source branch to pick up changes from.
  """
  exists, is_current, unused_tracks = branch_lib.status(src)
  if not exists:
    return (SRC_NOT_FOUND, None)
  if exists and is_current:
    return (SRC_IS_CURRENT_BRANCH, None)
  ret, out = sync.merge(src)
  if ret is sync.SUCCESS:
    return (SUCCESS, out)
  elif ret is sync.LOCAL_CHANGES_WOULD_BE_LOST:
    return (LOCAL_CHANGES_WOULD_BE_LOST, out)
  elif ret is sync.NOTHING_TO_MERGE:
    return (NOTHING_TO_MERGE, out)
  raise Exception("Unexpected ret code %s" % ret)


def merge_in_progress():
  return sync.merge_in_progress()


def was_resolved(fp):
  """Returns True if the given file had conflicts and was marked as resolved."""
  return os.path.exists(_resolved_file(fp))


def resolve(fp):
  """Marks the given file in conflict as resolved.

  Args:
    fp: the file to mark as resolved.

  Returns:
    - FILE_NOT_FOUND
    - FILE_NOT_IN_CONFLICT
    - SUCCESS
  """
  if not os.path.exists(fp):
    return FILE_NOT_FOUND

  s = status.of_file(fp)
  if s is not status.IN_CONFLICT:
    return FILE_NOT_IN_CONFLICT

  # In Git, to mark a file as resolved we have to add it.
  file.stage(fp)
  # We add a file in the Gitless directory to be able to tell when a file has
  # been marked as resolved.
  # TODO(sperezde): might be easier to just find a way to tell if the file is
  # in the index.
  open(_resolved_file(fp), 'w').close()
  return SUCCESS


def _resolved_file(fp):
  return os.path.join(lib.gl_dir(), '.GL_%s_%s' % (branch_lib.current(), fp))
