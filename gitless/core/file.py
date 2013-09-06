# Gitless - a version control system built on top of Git.
# Copyright (c) 2013  Santiago Perez De Rosso.
# Licensed under GNU GPL, version 2.

"""Gitless's file lib."""


import collections
import os
import re

from gitpylib import file as git_file
from gitpylib import status as git_status

import repo as repo_lib
import branch as branch_lib


SUCCESS = 1
FILE_NOT_FOUND = 2
FILE_ALREADY_TRACKED = 3
FILE_ALREADY_UNTRACKED = 4
FILE_IS_UNTRACKED = 5
FILE_NOT_FOUND_AT_CP = 6
FILE_IN_CONFLICT = 7
FILE_IS_IGNORED = 8
FILE_NOT_IN_CONFLICT = 9
FILE_ALREADY_RESOLVED = 10

# Possible type of files.
TRACKED = 11
UNTRACKED = 12
IGNORED = 13


def track(fp):
  """Start tracking changes to fp.

  Args:
      fp: The file path of the file to track.

  Returns:
      - FILE_NOT_FOUND: the given file was not found;
      - FILE_ALREADY_TRACKED: the given file is already a tracked file;
      - FILE_IS_IGNORED: the given file is an ignored file;
      - SUCCESS: the operation finished sucessfully.
  """
  s = git_status.of_file(fp)
  if s is git_status.FILE_NOT_FOUND:
    return FILE_NOT_FOUND
  elif _is_tracked_status(s):
    return FILE_ALREADY_TRACKED
  elif _is_ignored_status(s):
    return FILE_IS_IGNORED

  # If we reached this point we know that the file to track is a untracked
  # file. This means that in the Git world, the file could be either:
  #   (i)  a new file for Git => add the file.
  #   (ii) an assumed unchanged file => unmark it.
  s = git_status.of_file(fp)
  if s is git_status.UNTRACKED:
    # Case (i).
    git_file.stage(fp)
  elif (s is git_status.ASSUME_UNCHANGED or
        s is git_status.DELETED_ASSUME_UNCHANGED):
    # Case (ii).
    git_file.not_assume_unchanged(fp)
  else:
    raise Exception("File %s in unkown status %s" % (fp, s))

  return SUCCESS


def untrack(fp):
  """Stop tracking changes to fp.

  Args:
      fp: The file path of the file to untrack.

  Returns:
      - FILE_NOT_FOUND: the given file was not found;
      - FILE_ALREADY_UNTRACKED: the given file is already an untracked file;
      - SUCCESS: the operation finished sucessfully;
      - FILE_IN_CONFLICT: the file is in conflict;
      - FILE_IS_IGNORED: the file is ignored.
  """
  s = git_status.of_file(fp)
  if s is git_status.FILE_NOT_FOUND:
    return FILE_NOT_FOUND
  elif _is_ignored_status(s):
    return FILE_IS_IGNORED
  elif not _is_tracked_status(s):
    return FILE_ALREADY_UNTRACKED

  # If we reached this point we know that the file to untrack is a tracked
  # file. This means that in the Git world, the file could be either:
  #   (i)  a new file for Git that is staged (the user executed gl track on a
  #        uncomitted file) => reset changes;
  #   (ii) the file is a previously committed file => mark it as assumed
  #        unchanged.
  if s is git_status.STAGED:
    # Case (i).
    git_file.unstage(fp)
  elif (s is git_status.TRACKED_UNMODIFIED or
        s is git_status.TRACKED_MODIFIED or
        s is git_status.DELETED):
    # Case (ii).
    git_file.assume_unchanged(fp)
  elif s is git_status.IN_CONFLICT:
    return FILE_IN_CONFLICT
  else:
    raise Exception("File %s in unkown status %s" % (fp, s))

  return SUCCESS


def diff(fp):
  """Compute the diff of the given file with its last committed version.

  Args:
    fp: The file path of the file to diff.

  Returns:
    A pair (result, out) where result is one of:
      - FILE_NOT_FOUND: the given file was not found;
      - FILE_IS_UNTRACKED: the given file is an untracked file;
      - SUCCESS: the operation finished sucessfully.
    and out is the output of the diff command.
  """
  # TODO(sperezde): process the output of the diff command and return it in a
  # friendlier way.

  s = git_status.of_file(fp)
  if s is git_status.FILE_NOT_FOUND:
    return (FILE_NOT_FOUND, '')
  elif not _is_tracked_status(s):
    return (FILE_IS_UNTRACKED, '')

  out = ''
  if s is git_status.STAGED:
    diff_out = git_file.staged_diff(fp)
    out = "\n".join(diff_out.splitlines()[5:])
  elif s is git_status.ADDED_MODIFIED or s is git_status.MODIFIED_MODIFIED:
    git_file.stage(fp)
    diff_out = git_file.staged_diff(fp)
    out = "\n".join(diff_out.splitlines()[5:])
  elif s is git_status.DELETED:
    diff_out = git_file.diff(fp)
    out = "\n".join(diff_out.splitlines()[5:])
  else:
    diff_out = git_file.diff(fp)
    out = "\n".join(diff_out.splitlines()[4:])

  return (SUCCESS, out)


def is_tracked(fp):
  """True if the given file is a tracked file."""
  return _is_tracked_status(git_status.of_file(fp))


def is_tracked_modified(fp):
  """True if the given file is a tracked file with modifications."""
  s = git_status.of_file(fp)
  return _is_tracked_status(s) and not s is git_status.TRACKED_UNMODIFIED


def is_deleted(fp):
  """True if the given file is a deleted file."""
  return _is_deleted_status(git_status.of_file(fp))


def checkout(fp, cp):
  """Checkouts file fp at cp.

  Args:
    fp: the filepath to checkout.
    cp: the commit point at which to checkout the file.

  Returns:
    a pair (status, out) where status is one of FILE_NOT_FOUND_AT_CP or SUCCESS
    and out is the content of fp at cp.
  """
  # "show" expects the full path with respect to the repo root.
  rel_fp = os.path.join(repo_lib.cwd(), fp)[1:]
  ret, out = git_file.show(rel_fp, cp)

  if ret is git_file.FILE_NOT_FOUND_AT_CP:
    return (FILE_NOT_FOUND_AT_CP, None)

  s = git_status.of_file(fp)
  unstaged = False
  if s is git_status.STAGED:
    git_file.unstage(fp)
    unstaged = True

  dst = open(fp, 'w')
  dst.write(out)
  dst.close()

  if unstaged:
    git_file.stage(fp)

  return (SUCCESS, out)


def status(fp):
  """Gets the status of fp.
  
  Args:
    fp: the file to status.

  Returns:
    a named tuple (fp, type, exists_in_lr, exists_in_wd, modified, in_conflict,
    resolved) where fp is a file path type is one of TRACKED, UNTRACKED or
    IGNORED and all the remaining fields are booleans. The in_conflict and
    resolved fields are only applicable if the file is TRACKED.
  """
  return _build_f_st(*git_status.of_repo())


def status_all():
  """Gets the status of all files relative to the cwd.

  Returns:
    a list of named tuples (fp, type, exists_in_lr, exists_in_wd, modified,
    in_conflict, resolved) where fp is a file path type is one of TRACKED,
    UNTRACKED or IGNORED and all the remaining fields are booleans. The
    in_conflict and resolved fields are only applicable if the file is TRACKED.
  """
  return [_build_f_st(s, fp) for (s, fp) in git_status.of_repo()]


def _build_f_st(s, fp):
  FileStatus = collections.namedtuple(
      'FileStatus', [
        'fp', 'type', 'exists_in_lr', 'exists_in_wd', 'modified', 'in_conflict',
        'resolved'])
  if s is git_status.TRACKED_UNMODIFIED:
    return FileStatus(fp, TRACKED, True, True, False, False, False)
  elif s is git_status.TRACKED_MODIFIED:
    return FileStatus(fp, TRACKED, True, True, True, False, was_resolved(fp))
  elif s is git_status.STAGED:
    # Staged file don't exist in the lr for Gitless.
    return FileStatus(fp, TRACKED, False, True, True, False, False)
  elif s is git_status.ASSUME_UNCHANGED:
    return FileStatus(fp, UNTRACKED, True, True, True, False, False)
  elif s is git_status.DELETED:
    return FileStatus(fp, TRACKED, True, False, True, False, was_resolved(fp))
  elif s is git_status.DELETED_STAGED:
    # This can only happen if the user did a rm of a new file. The file doesn't
    # exist anymore for Gitless.
    git_file.unstage(fp)
  elif s is git_status.DELETED_ASSUME_UNCHANGED:
    return FileStatus(fp, UNTRACKED, True, False, True, False, False)
  elif s is git_status.IN_CONFLICT:
    return FileStatus(fp, TRACKED, True, True, True, True, was_resolved(fp))
  elif s is git_status.IGNORED or s is git_status.IGNORED_STAGED:
    return FileStatus(fp, IGNORED, True, True, True, True, False)
  elif s is git_status.MODIFIED_MODIFIED:
    # The file was marked as resolved and then modified. To Gitless, this is
    # just a regular tracked file.
    return FileStatus(fp, TRACKED, True, True, True, False, was_resolved(fp))
  elif s is git_status.ADDED_MODIFIED:
    # The file is a new file that was added and then modified. This can only
    # happen if the user gl tracks a file and then modifies it.
    return FileStatus(fp, TRACKED, True, True, True, False, False)
  return FileStatus(fp, UNTRACKED, False, True, True, False, False)


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
  s = git_status.of_file(fp)
  if not os.path.exists(fp) and not (s is git_status.IN_CONFLICT):
    return FILE_NOT_FOUND

  if s is not git_status.IN_CONFLICT:
    return FILE_NOT_IN_CONFLICT

  if is_resolved_file(fp):
    return FILE_ALREADY_RESOLVED

  # In Git, to mark a file as resolved we have to add it.
  git_file.stage(fp)
  # We add a file in the Gitless directory to be able to tell when a file has
  # been marked as resolved.
  # TODO(sperezde): might be easier to just find a way to tell if the file is
  # in the index.
  open(_resolved_file(fp), 'w').close()
  return SUCCESS


def internal_resolved_cleanup():
  for f in os.listdir(repo_lib.gl_dir()):
    if f.startswith('GL_RESOLVED'):
      os.remove(os.path.join(repo_lib.gl_dir(), f))
      #print 'removed %s' % f


def resolved_files():
  ret = []
  for f in os.listdir(repo_lib.gl_dir()):
    match = re.match('GL_RESOLVED_\w+_(\w+)', f)
    if match:
      ret.append(match.group(1))
  return ret


def is_resolved_file(fp):
  return fp in resolved_files()


# Private methods.


def _is_tracked_status(s):
  """True if the given status corresponds to a gl tracked file."""
  return (
      s is git_status.TRACKED_UNMODIFIED or
      s is git_status.TRACKED_MODIFIED or
      s is git_status.STAGED or
      s is git_status.IN_CONFLICT or
      s is git_status.DELETED or
      s is git_status.MODIFIED_MODIFIED or
      s is git_status.ADDED_MODIFIED)


def _is_deleted_status(s):
  """True if the given status corresponds to a gl deleted file."""
  return s is git_status.DELETED


def _is_ignored_status(s):
  """True if the given status corresponds to a gl ignored file."""
  return s is git_status.IGNORED


def _resolved_file(fp):
  return os.path.join(
      repo_lib.gl_dir(), 'GL_RESOLVED_%s_%s' % (branch_lib.current(), fp))
