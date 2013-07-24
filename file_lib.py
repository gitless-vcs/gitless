# Gitless - a version control system built on top of Git.
# Copyright (c) 2013  Santiago Perez De Rosso.
# Licensed under GNU GPL, version 2.

"""Gitless's file lib."""


import os

from gitpylib import file as git_file
from gitpylib import status as git_status


SUCCESS = 1
FILE_NOT_FOUND = 2
FILE_ALREADY_TRACKED = 3
FILE_ALREADY_UNTRACKED = 4
FILE_IS_UNTRACKED = 5
FILE_NOT_FOUND_AT_CP = 6
FILE_IN_CONFLICT = 7
FILE_IS_IGNORED = 8


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
  if not os.path.exists(fp):
    return FILE_NOT_FOUND

  s = git_status.of_file(fp)
  if _is_tracked_status(s):
    return FILE_ALREADY_TRACKED
  if _is_ignored_status(s):
    return FILE_IS_IGNORED

  if os.path.isdir(fp) and not os.listdir(fp):
    # fp is a directory and is empty; we need to do some magic for Git to
    # track it.
    # TODO(sperezde): Implement this.
    # print 'Dir is empty!'
    return SUCCESS
 
  # If we reached this point we know that the file to track is a untracked
  # file. This means that in the Git world, the file could be either:
  #   (i)  a new file for Git => add the file.
  #   (ii) an assumed unchanged file => unmark it.
  s = git_status.of_file(fp)
  if s is git_status.UNTRACKED:
    # Case (i).
    git_file.stage(fp)
  elif s is git_status.ASSUME_UNCHANGED:
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
  if not os.path.exists(fp):
    return FILE_NOT_FOUND

  s = git_status.of_file(fp)
  if _is_ignored_status(s):
    return FILE_IS_IGNORED

  if not _is_tracked_status(s):
    return FILE_ALREADY_UNTRACKED

  if os.path.isdir(fp) and not os.listdir(fp):
    # fp is a directory and is empty; we need to do some magic for Git to
    # untrack it.
    # TODO(sperezde): Implement this.
    # print 'Dir is empty!'
    return SUCCESS

  # If we reached this point we know that the file to untrack is a tracked
  # file. This means that in the Git world, the file could be either:
  #   (i)  a new file for Git that is staged (the user executed gl track on a
  #        uncomitted file) => reset changes;
  #   (ii) the file is a previously committed file => mark it as assumed
  #        unchanged.
  s = git_status.of_file(fp)
  if s is git_status.STAGED:
    # Case (i).
    git_file.unstage(fp)
  elif (s is git_status.TRACKED_UNMODIFIED) or (s is git_status.TRACKED_MODIFIED):
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
  if not os.path.exists(fp):
    return (FILE_NOT_FOUND, '')

  s = git_status.of_file(fp)
  if not _is_tracked_status(s):
    return (FILE_IS_UNTRACKED, '')

  out = ''
  if s is git_status.STAGED:
    diff_out = git_file.staged_diff(fp)[1]
    out = "\n".join(diff_out.splitlines()[5:])
  elif s is git_status.ADDED_MODIFIED or s is git_status.MODIFIED_MODIFIED:
    git_file.stage(fp)
    diff_out = git_file.staged_diff(fp)[1]
    out = "\n".join(diff_out.splitlines()[5:])
  else:
    diff_out = git_file.diff(fp)[1]
    out = "\n".join(diff_out.splitlines()[4:])

  return (SUCCESS, out)


def is_tracked_file(fp):
  """True if the given file is a tracked file."""
  return _is_tracked_status(git_status.of_file(fp))


def is_tracked_modified(fp):
  """True if the given file is a tracked file with modifications."""
  s = git_status.of_file(fp)
  return _is_tracked_status(s) and not s is git_status.TRACKED_UNMODIFIED


def is_deleted_file(fp):
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
  ret, out = git_file.show(fp, cp)
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


def rm(fp):
  """Removes the given file.
 
  Args:
    fp: the file path of the file to remove.

  Returns:
    - FILE_NOT_FOUND: the given file was not found;
    - FILE_IS_UNTRACKED: the given file is an untracked file;
    - SUCCESS: the operation finished sucessfully.
  """
  if not os.path.exists(fp):
    return FILE_NOT_FOUND

  if not is_tracked_file(fp):
    return FILE_IS_UNTRACKED

  s = git_status.of_file(fp)

  if s is git_status.STAGED:
    git_file.unstage(fp)
 
  os.remove(fp)
  return SUCCESS


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
