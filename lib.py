"""Gitless's lib."""

import os.path
import subprocess


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
  out, unused_err = _safe_git_call('status --porcelain %s' % fp)
  if len(out) > 0 and out[0] is '?':
    # Case (i).
    cmd = 'add %s'
  else:
    # Case (ii).
    cmd = 'update-index --no-assume-unchanged %s'

  _safe_git_call(cmd  % fp)
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
  out, unused_err = _safe_git_call('status --porcelain %s' % fp)
  if len(out) > 0 and out[0] is 'A':
    # Case (i).
    # "git reset" currently returns 0 (if successful) while "git reset
    # $pathspec" returns 0 iff the index matches HEAD after resetting (on
    # all paths, not just those matching $pathspec). See
    # http://comments.gmane.org/gmane.comp.version-control.git/211242.
    # So, we need to ignore the return code (unfortunately) and hope that it
    # works.
    _git_call('reset HEAD %s' % fp)
  else:
    # Case (ii).
    _safe_git_call('update-index --assume-unchanged %s' % fp)
  return SUCCESS


def is_tracked_file(fp):
  # ls-files will succeed if the file to be listed has been added or if it is
  # what Git understands as a tracked file (a file which has been committed).
  # But we also need to detect if the file is an assumed-unchanged file (-v
  # option) since this is a untracked file to Gitless.
  ok, out, unused_err = _git_call(
      'ls-files -v --error-unmatch %s' % fp)
  if not ok:
    # The file doesn't even exist or hasn't been added => not a Gitless's
    # tracked file.
    return False
  else:
    # If it's an assumed-unchanged file => not a Gitless's tracked file.
    # assumed-unchanged files appear listed with a lower-case letter.
    return out[0].isupper()

def _safe_git_call(cmd):
  ok, out, err = _git_call(cmd)
  if ok:
    return out, err
  raise Exception('%s failed: out is %s, err is %s' % (cmd, out, err))

def _git_call(cmd):
  with open(os.devnull, "w") as f_null:
    p = subprocess.Popen(
        'git %s' % cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        shell=True)
    out, err = p.communicate()
    return p.returncode == 0, out, err
