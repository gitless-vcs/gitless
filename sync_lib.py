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
MERGE_NOT_IN_PROGRESS = 8
CONFLICT = 9
REBASE_NOT_IN_PROGRESS = 10
NOTHING_TO_REBASE = 11


def merge(src):
  """Merges changes in the src branch into the current branch.

  Args:
    src: the source branch to pick up changes from.
  """
  is_valid, error = _valid_branch(src)
  if not is_valid:
    return (error, None)

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


def abort_merge():
  if not merge_in_progress():
    return MERGE_NOT_IN_PROGRESS
  sync.abort_merge()
  internal_resolved_cleanup()
  return SUCCESS


def rebase(new_base):
  is_valid, error = _valid_branch(new_base)
  if not is_valid:
    return (error, None)

  current = branch_lib.current()
  ret, out = sync.rebase(new_base)
  if ret is sync.SUCCESS:
    return (SUCCESS, out)
  elif ret is sync.LOCAL_CHANGES_WOULD_BE_LOST:
    return (LOCAL_CHANGES_WOULD_BE_LOST, out)
  elif ret is sync.CONFLICT:
    # We write a file to note the current branch being rebased and the new base.
    _write_rebase_file(current, new_base)
    return (CONFLICT, out)
  elif ret is sync.NOTHING_TO_REBASE:
    return (NOTHING_TO_REBASE, out)
  raise Exception("Unexpected ret code %s" % ret)


def rebase_in_progress():
  return os.path.exists(os.path.join(lib.gl_dir(), 'GL_REBASE'))


def rebase_info():
  """Gets the name of the current branch being rebased and the new base."""
  rf = open(_rebase_file(), 'r')
  current = rf.readline().strip()
  new_base = rf.readline().strip()
  return (current, new_base)


def abort_rebase():
  if not rebase_in_progress():
    return REBASE_NOT_IN_PROGRESS
  sync.abort_rebase()
  conclude_rebase()
  return SUCCESS


def skip_rebase_commit():
  if not rebase_in_progress():
    return REBASE_NOT_IN_PROGRESS
  s = sync.skip_rebase_commit()
  if s[0] is sync.SUCCESS:
    conclude_rebase()
    return (SUCCESS, s[1])
  elif s[0] is sync.CONFLICT:
    return (SUCCESS, s[1])
  else:
    raise Exception('Unrecognized ret code %s' % s[0])


def conclude_rebase():
  internal_resolved_cleanup()
  os.remove(_rebase_file())


def _write_rebase_file(current, new_base):
  rf = open(_rebase_file(), 'w')
  rf.write(current + '\n')
  rf.write(new_base + '\n')
  rf.close()


def _rebase_file():
  return os.path.join(lib.gl_dir(), 'GL_REBASE')

 
def _valid_branch(b):
  exists, is_current, unused_tracks = branch_lib.status(b)
  if not exists:
    return (False, SRC_NOT_FOUND)
  if exists and is_current:
    return (False, SRC_IS_CURRENT_BRANCH)
  return (True, None)


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


def internal_resolved_cleanup():
  for f in os.listdir(lib.gl_dir()):
    if f.startswith('GL_RESOLVED'):
      os.remove(os.path.join(lib.gl_dir(), f))
      print 'removed %s' % f


def _resolved_file(fp):
  return os.path.join(lib.gl_dir(), 'GL_RESOLVED_%s_%s' % (branch_lib.current(), fp))
