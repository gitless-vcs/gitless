"""Gitless's lib."""

import os.path
import subprocess

from gitpylib import file
from gitpylib import status


SUCCESS = 1
FILE_NOT_FOUND = 2
FILE_ALREADY_TRACKED = 3
FILE_ALREADY_UNTRACKED = 4


def track_file(fp):
  """Start tracking changes to fp.

  Makes fp a tracked file; fp can be a file or a directory. If
  it is a directory, all the contents of the directory will be recursively
  tracked. If it is an empty directory, the directory will also be tracked (can
  be committed/pushed). Creating new files under tracked directories don't
  automatically make these tracked files; they need to be explicitly tracked.

  Args:
      fp: The file path of the file to track.

  Returns:
      FILE_NOT_FOUND: the given file was not found;
      FILE_ALREADY_TRACKED: the given file is already a tracked file;
      SUCCESS: the operation finished sucessfully.
  """
  if not os.path.exists(fp):
    return FILE_NOT_FOUND

  if _is_tracked_file(fp):
    return FILE_ALREADY_TRACKED

  if os.path.isdir(fp) and not os.listdir(fp):
    # fp is a directory and is empty; we need to do some magic for Git to
    # track it.
    # TODO(sperezde): Implement this.
    print 'Dir is empty!'
    return SUCCESS
 
  # If we reached this point we know that the file to track is a untracked
  # file. This means that in the Git world, the file could be either:
  #   (i)  a new file for Git => add the file.
  #   (ii) an assumed unchanged file => unmark it.
  s = status.of_file(fp)
  if s is status.UNTRACKED:
    # Case (i).
    file.stage(fp)
  elif s is status.ASSUME_UNCHANGED:
    # Case (ii).
    file.not_assume_unchanged(fp)
  else:
    raise Exception("File %s in unkown status %s" % (fp, s))

  return SUCCESS


def untrack_file(fp):
  """Stop tracking changes to fp.

  Makes fp an untracked file; fp can be a file or a directory. If
  it is a directory, all the contents of the directory will be recursively
  untracked. If it is an empty directory, the directory will also be untracked.

  Args:
      fp: The file path of the file to untrack.

  Returns:
      FILE_NOT_FOUND: the given file was not found;
      FILE_ALREADY_UNTRACKED: the given file is already an untracked file;
      SUCCESS: the operation finished sucessfully.
  """
  if not os.path.exists(fp):
    return FILE_NOT_FOUND

  if not _is_tracked_file(fp):
    return FILE_ALREADY_UNTRACKED

  if os.path.isdir(fp) and not os.listdir(fp):
    # fp is a directory and is empty; we need to do some magic for Git to
    # untrack it.
    # TODO(sperezde): Implement this.
    print 'Dir is empty!'
    return SUCCESS

  # If we reached this point we know that the file to untrack is a tracked
  # file. This means that in the Git world, the file could be either:
  #   (i)  a new file for Git that is staged (the user executed gl track on a
  #        uncomitted file) => reset changes;
  #   (ii) the file is a previously committed file => mark it as assumed
  #        unchanged.
  s = status.of_file(fp)
  if s is status.STAGED:
    # Case (i).
    file.unstage(fp)
  elif s is (status.TRACKED_UNMODIFIED or status.TRACKED_MODIFIED):
    # Case (ii).
    file.assume_unchanged(fp)
  else:
    raise Exception("File %s in unkown status %s" % (fp, s))

  return SUCCESS


def _is_tracked_file(fp):
  """True if the given file is a tracked file."""
  s = status.of_file(fp)
  return (
      s is status.TRACKED_UNMODIFIED or
      s is status.TRACKED_MODIFIED or
      s is status.STAGED)
