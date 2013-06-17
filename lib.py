"""Gitless's lib."""

import os.path
import subprocess

from gitpylib import common
from gitpylib import file
from gitpylib import status
from gitpylib import sync


SUCCESS = 1
FILE_NOT_FOUND = 2
FILE_ALREADY_TRACKED = 3
FILE_ALREADY_UNTRACKED = 4
FILE_IS_UNTRACKED = 5


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
      - FILE_NOT_FOUND: the given file was not found;
      - FILE_ALREADY_TRACKED: the given file is already a tracked file;
      - SUCCESS: the operation finished sucessfully.
  """
  if not os.path.exists(fp):
    return FILE_NOT_FOUND

  if is_tracked_file(fp):
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
      - FILE_NOT_FOUND: the given file was not found;
      - FILE_ALREADY_UNTRACKED: the given file is already an untracked file;
      - SUCCESS: the operation finished sucessfully.
  """
  if not os.path.exists(fp):
    return FILE_NOT_FOUND

  if not is_tracked_file(fp):
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
  elif (s is status.TRACKED_UNMODIFIED) or (s is status.TRACKED_MODIFIED):
    # Case (ii).
    file.assume_unchanged(fp)
  else:
    raise Exception("File %s in unkown status %s" % (fp, s))

  return SUCCESS


def repo_status():
  """Gets the status of the repo.
  
  Returns:
      A pair (tracked_mod_list, untracked_list) where each list contain a pair
      (fp, exists_in_lr); fp a filepath and exists_in_lr is a boolean that is
      True if the file exists in the local repo.
  """
  # TODO(sperezde): Will probably need to implement this smarter in the future.
  # TODO(sperezde): using frozenset should improve performance.
  tracked_mod_list = []
  untracked_list = []
  for (s, fp) in status.of_repo():
    if s is status.TRACKED_UNMODIFIED:
      # We don't return tracked unmodified files.
      continue

    if s is status.TRACKED_MODIFIED:
      tracked_mod_list.append((fp, True))
    elif s is status.STAGED:
      tracked_mod_list.append((fp, False))
    elif s is status.ASSUME_UNCHANGED:
      untracked_list.append((fp, True))
    else:
      untracked_list.append((fp, False))

  return (tracked_mod_list, untracked_list)


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
  if not os.path.exists(fp):
    return (FILE_NOT_FOUND, '')

  if not is_tracked_file(fp):
    return (FILE_IS_UNTRACKED, '')

  return (SUCCESS, file.diff(fp)[1])


def commit(files, msg):
  """Record changes in the local repository.
  
  Args:
    files: the files to commit.
    msg: the commit message.

  Returns:
    The output of the commit command.
  """
  return sync.commit(files, msg)


def is_tracked_file(fp):
  """True if the given file is a tracked file."""
  return _is_tracked_status(status.of_file(fp))


def _is_tracked_status(s):
  """True if the given status corresponds to a gl tracked file."""
  return (
      s is status.TRACKED_UNMODIFIED or
      s is status.TRACKED_MODIFIED or
      s is status.STAGED)


def reset(fp, cp):
  """Resets the given file to the given commit point.
  
  Args:
    fp: the filepath of the file to reset.
    cp: the commit point to reset the file to. (e.g., 'HEAD', some sha1)
  
  Returns:
    - FILE_NOT_FOUND: the given file was not found;
    - FILE_IS_UNTRACKED: the given file is an untracked file;
    - SUCCESS: the operation finished sucessfully.
  """
  if not os.path.exists(fp):
    return FILE_NOT_FOUND

  s = status.of_file(fp)

  if not _is_tracked_status(s):
    return FILE_IS_UNTRACKED

  if s is status.STAGED:
    # We unstage it, and remove it.
    # TODO(sperezde): show error if cp != HEAD
    file.unstage(fp)
    os.remove(fp)
  else:
    # We simply clobber the file with its content at cp.
    file.show(fp, cp, fp)
  return SUCCESS


def gl_dir():
  """Gets the path to the gl directory.
  
  Returns:
    The absolute path to the gl directory or None if the current working
    directory is not a Gitless repository.
  """
  # We use the same .git directory.
  return common.git_dir()
