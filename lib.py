"""Gitless's lib."""

import os.path
import subprocess

from gitpylib import common
from gitpylib import file
from gitpylib import status
from gitpylib import sync
import sync_lib


SUCCESS = 1
FILE_NOT_FOUND = 2
FILE_ALREADY_TRACKED = 3
FILE_ALREADY_UNTRACKED = 4
FILE_IS_UNTRACKED = 5
FILE_NOT_FOUND_AT_CP = 6
UNRESOLVED_CONFLICTS = 7


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
      A pair (tracked_mod_list, untracked_list) where
      - tracked_mod_list: contains a tuple (fp, exists_in_lr, exists_in_wd, in_conflict)
      - untracked_list: contains a pair (fp, exists_in_lr).
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
      tracked_mod_list.append((fp, True, True, False))
    elif s is status.STAGED:
      tracked_mod_list.append((fp, False, True, False))
    elif s is status.ASSUME_UNCHANGED:
      untracked_list.append((fp, True, False))
    elif s is status.DELETED:
      tracked_mod_list.append((fp, True, False, False))
    elif s is status.DELETED_STAGED:
      # The user broke the gl interface layer by using /usr/bin/rm directly.
      raise Exception('Got a DELETED_STAGED status for %s' % fp)
    elif s is status.DELETED_ASSUME_UNCHANGED:
      # The user broke the gl interface layer by using /usr/bin/rm directly.
      raise Exception('Got a DELETED_ASSUME_UNCHANGED status for %s' % fp)
    elif s is status.IN_CONFLICT:
      # TODO: check what happens with deletion conflicts.
      tracked_mod_list.append((fp, True, True, True))
    else:
      untracked_list.append((fp, False))

  return (tracked_mod_list, untracked_list)


def rm(fp):
  """Removes the given file
 
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

  s = status.of_file(fp)

  if s is status.STAGED:
    file.unstage(fp)
 
  os.remove(fp)
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
    a pair (status, out) where status can be:
    - UNRESOLVED_CONFLICTS -> out is the list of unresolved files.
    - SUCCESS -> out is the output of the commit command.
  """
  if sync_lib.merge_in_progress():
    # If we are doing a merge then we can't do a partial commit (Git won't let
    # us do it). We can do commit -i which will stage all the files but we need
    # to watch out for not commiting new Gitless's tracked files that are not in
    # the list.
    # To do this, we temporarily unstage these files and then re-stage them
    # after the commit.
    # TODO(sperezde): actually implement what the comment above says ;)
    # TODO(sperezde): also need to do something with deletions?
    unresolved = []
    for fp, exists_in_lr, exists_in_wd, in_conflict in repo_status()[0]:
      if in_conflict:
        unresolved.append(fp)

    if unresolved:
      return (UNRESOLVED_CONFLICTS, unresolved)
    print 'commiting files %s' % files
    return (SUCCESS, sync.commit_include(files, msg))
  return (SUCCESS, sync.commit(files, msg))


def is_tracked_file(fp):
  """True if the given file is a tracked file."""
  return _is_tracked_status(status.of_file(fp))


def _is_tracked_status(s):
  """True if the given status corresponds to a gl tracked file."""
  return (
      s is status.TRACKED_UNMODIFIED or
      s is status.TRACKED_MODIFIED or
      s is status.STAGED or
      s is status.IN_CONFLICT)


# TODO(sperezde): does this still work if the file was moved?
def checkout(fp, cp):
  """Checkouts file fp at cp.
  
  Args:
    fp: the filepath to checkout.
    cp: the commit point at which to checkout the file.
 
  Returns:
    a pair (status, out) where status is one of FILE_NOT_FOUND_AT_CP or SUCCESS
    and out is the content of fp at cp.
  """
  ret, out = file.show(fp, cp)
  if ret is file.FILE_NOT_FOUND_AT_CP:
    return (FILE_NOT_FOUND_AT_CP, None)

  return (SUCCESS, out)


def gl_dir():
  """Gets the path to the gl directory.
  
  Returns:
    The absolute path to the gl directory or None if the current working
    directory is not a Gitless repository.
  """
  # We use the same .git directory.
  return common.git_dir()
