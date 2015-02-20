# Gitless - a version control system built on top of Git.
# Licensed under GNU GPL v2.

"""Gitless's file lib."""


import collections
import os

from gitless.gitpylib import common as git_common
from gitless.gitpylib import file as git_file
from gitless.gitpylib import status as git_status

from . import core


# Ret codes of methods.
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
FILE_IS_DIR = 11

# Possible Gitless's file types.
TRACKED = 12
UNTRACKED = 13
IGNORED = 14

# Possible diff output lines.
DIFF_INFO = git_file.DIFF_INFO  # line carrying diff info for new hunk.
DIFF_SAME = git_file.DIFF_SAME  # line that git diff includes for context.
DIFF_ADDED = git_file.DIFF_ADDED
DIFF_MINUS = git_file.DIFF_MINUS


def track(fp):
  """Start tracking changes to fp.

  Args:
    fp: the file path of the file to track.

  Returns:
    FILE_NOT_FOUND, FILE_IS_DIR, FILE_ALREADY_TRACKED, FILE_IN_CONFLICT,
    FILE_IS_IGNORED or SUCCESS.
  """
  if os.path.isdir(fp):
    return FILE_IS_DIR
  gl_st, git_s = _status(fp)
  if not gl_st:
    return FILE_NOT_FOUND
  elif gl_st.type == TRACKED:
    return FILE_ALREADY_TRACKED
  elif gl_st.type == IGNORED:
    return FILE_IS_IGNORED

  # If we reached this point we know that the file to track is a untracked
  # file. This means that in the Git world, the file could be either:
  #   (i)  a new file for Git => add the file.
  #   (ii) an assumed unchanged file => unmark it.
  if git_s == '??':
    # Case (i).
    git_file.stage(fp)
  elif git_s == '  h':
    # Case (ii).
    git_file.not_assume_unchanged(fp)
  else:
    raise Exception('File {0} in unkown status {1}'.format(fp, git_s))

  return SUCCESS


def untrack(fp):
  """Stop tracking changes to fp.

  Args:
    fp: the file path of the file to untrack.

  Returns:
    FILE_NOT_FOUND, FILE_IS_DIR, FILE_ALREADY_UNTRACKED, FILE_IN_CONFLICT,
    FILE_IS_IGNORED or SUCCESS.
  """
  if os.path.isdir(fp):
    return FILE_IS_DIR
  gl_st, git_s = _status(fp)
  if not gl_st:
    return FILE_NOT_FOUND
  elif gl_st.type == IGNORED:
    return FILE_IS_IGNORED
  elif gl_st.type == UNTRACKED:
    return FILE_ALREADY_UNTRACKED

  # If we reached this point we know that the file to untrack is a tracked
  # file. This means that in the Git world, the file could be either:
  #   (i)  a new file for Git that is staged (the user executed gl track on a
  #        uncomitted file) => reset changes;
  #   (ii) the file is a previously committed file => mark it as assumed
  #        unchanged.
  if git_s == 'A H':
    # Case (i).
    git_file.unstage(fp)
  elif git_s.endswith('H'):
    # Case (ii).
    git_file.assume_unchanged(fp)
  elif git_s.startswith(('AA', 'M ', 'DD')) or 'U' in git_s:
    return FILE_IN_CONFLICT
  else:
    raise Exception('File {0} in unkown status {1}'.format(fp, git_s))

  return SUCCESS


def diff(fp):
  """Compute the diff of the given file with its last committed version.

  Args:
    fp: the file path of the file to diff.

  Returns:
    a pair (result, out) where result is one of FILE_NOT_FOUND,
    FILE_IS_UNTRACKED, FILE_IS_DIR or SUCCESS and out is the output of the diff
    command in a machine-friendly way: it's a tuple of the form
    (list of namedtuples with fields 'line', 'status', 'old_line_number',
     'new_line_number', line number padding, additions, deletions).
  """
  nil_out = (None, None, None, None)
  if os.path.isdir(fp):
    return FILE_IS_DIR, nil_out
  gl_st, git_s = _status(fp)
  if not gl_st:
    return FILE_NOT_FOUND, nil_out
  elif gl_st.type == UNTRACKED:
    return FILE_IS_UNTRACKED, nil_out
  elif gl_st.type == IGNORED:
    return FILE_IS_IGNORED, nil_out

  do_staged_diff = False
  if git_s == 'A H':
    do_staged_diff = True
  elif git_s == 'AMH' or git_s == 'MMH':
    git_file.stage(fp)
    do_staged_diff = True

  # Don't include the `git diff` header.
  return SUCCESS, git_file.diff(fp, staged=do_staged_diff)[:-1]


def checkout(fp, cp='HEAD'):
  """Checkouts file fp at cp.

  Args:
    fp: the filepath to checkout.
    cp: the commit point at which to checkout the file (defaults to HEAD).

  Returns:
    a pair (status, out) where status is one of FILE_IS_DIR,
    FILE_NOT_FOUND_AT_CP or SUCCESS and out is the content of fp at cp.
  """
  if os.path.isdir(fp):
    return FILE_IS_DIR, None

  repo = core.Repository()

  # "show" expects the path relative to the repo root
  rel_fp = os.path.relpath(os.path.abspath(fp), repo.root)
  ret, out = git_file.show(rel_fp, cp)

  if ret == git_file.FILE_NOT_FOUND_AT_CP:
    return FILE_NOT_FOUND_AT_CP, None

  _, s = _status(fp)
  unstaged = False
  if s == 'A H':
    git_file.unstage(fp)
    unstaged = True

  with open(fp, 'w') as dst:
    dst.write(out)

  if unstaged:
    git_file.stage(fp)

  return SUCCESS, out


def status(fp):
  """Gets the status of fp.

  Args:
    fp: the file to status (must be a file, no dirs).

  Returns:
    None (if the file wasn't found) or a named tuple (fp, type, exists_in_lr,
    exists_in_wd, modified, in_conflict, resolved) where fp is a file path, type
    is one of TRACKED, UNTRACKED or IGNORED and all the remaining fields are
    booleans. The modified field is True if the working version of the file
    differs from its committed version. (If there's no committed version,
    modified is set to True.)
  """
  return _status(fp)[0]


def status_all(only_paths=None, relative_paths=None):
  """Status of the repo or of the only_paths given.

  Args:
    only_paths: if given, only these paths will be considered.
    relative_paths: whether to output fps as relative paths from the cwd or
      from the repo root. If unset, the status.relativePaths config value is
      used (which is usually what you want).

  Returns:
    a list of named tuples (fp, type, exists_in_lr, exists_in_wd, modified,
    in_conflict, resolved) where fp is a file path, type is one of TRACKED,
    UNTRACKED or IGNORED and all the remaining fields are booleans. The
    modified field is True if the working version of the file differs from its
    committed version. (If there's no committed version, modified is set to
    True.)
  """
  for fp, s in git_status.of(
      only_paths=only_paths, relative_paths=relative_paths):
    f_st = _build_f_st(fp, s)
    if f_st:
      yield f_st


def resolve(fp):
  """Marks the given file in conflict as resolved.

  Args:
    fp: the file to mark as resolved.

  Returns:
    FILE_NOT_FOUND, FILE_NOT_IN_CONFLICT, FILE_ALREADY_RESOLVED or SUCCESS.
  """
  if os.path.isdir(fp):
    return FILE_IS_DIR
  f_st = status(fp)
  if not f_st:
    return FILE_NOT_FOUND
  if f_st.resolved:
    return FILE_ALREADY_RESOLVED
  if not f_st.in_conflict:
    return FILE_NOT_IN_CONFLICT

  # We don't use Git to keep track of resolved files, but just to make it feel
  # like doing a resolve in Gitless is similar to doing a resolve in Git
  # (i.e., add) we stage the file.
  git_file.stage(fp)
  # We add a file in the Gitless directory to be able to tell when a file has
  # been marked as resolved.
  open(_resolved_file(fp), 'w').close()
  return SUCCESS


def internal_resolved_cleanup():
  repo = core.Repository()
  gl_dir = repo.path
  for f in os.listdir(gl_dir):
    if f.startswith('GL_RESOLVED'):
      os.remove(os.path.join(gl_dir, f))
      #print 'removed %s' % f


# Private methods.


def _status(fp):
  """Get the status of the given fp.

  Returns:
    a tuple (gl_status, git_status) where gl_status is a FileStatus namedtuple
    representing the status of the file (or None if the file doesn't exist) and
    git_status is one of git's possible status for the file.
  """
  git_s = git_status.of_file(fp)
  if not git_s:
    return None, None
  gl_s = _build_f_st(fp, git_s)
  if not gl_s:
    return None, git_s
  return gl_s, git_s


st_map = {
    '??': (UNTRACKED, False, True, True, False, False),
    '  H': (TRACKED, True, True, False, False, False),
    ' MH': (TRACKED, True, True, True, False, False),
    # A file could have been "gl track"ed and later ignored by adding a matching
    # pattern in a .gitignore file. We consider this kind of file to still be a
    # tracked file. This is consistent with the idea that tracked files can't be
    # ignored.
    # TODO(sperezde): address the following rough edge: the user could untrack a
    # tracked file (one that was not committed before) and if it's matched by a
    # .gitignore file it will be ignored. The same thing won't happen if an
    # already committed file is untracked (due to how Gitless keeps track of
    # these kind of files).

    # Staged files don't exist in the lr for Gitless.
    'A H': (TRACKED, False, True, True, False, False),
    ' DH': (TRACKED, True, False, True, False, False),
    '!!': (IGNORED, False, True, True, True, False),
    'MMH': (TRACKED, True, True, True, False, True),
    'AMH': (TRACKED, False, True, True, False, False)}


FileStatus = collections.namedtuple(
    'FileStatus', [
        'fp', 'type', 'exists_in_lr', 'exists_in_wd', 'modified',
        'in_conflict', 'resolved'])


def _build_f_st(fp, s):
  ret = None
  try:
    ret = FileStatus(fp, *st_map[s])
  except KeyError:
    if s == 'ADH':
      # This can only happen if the user did a rm of a new file. The file
      # doesn't exist as far as Gitless is concerned.
      git_file.unstage(fp)
    elif s == '  h':
      # TODO: detect whether it is modified or not?
      if os.path.exists(fp):
        ret = FileStatus(fp, UNTRACKED, True, True, True, False, False)
    elif s.startswith(('AA', 'M ', 'DD')) or 'U' in s:
      wr = _was_resolved(fp)
      ret = FileStatus(fp, TRACKED, True, True, True, not wr, wr)
  return ret


def _was_resolved(fp):
  """Returns True if the given file had conflicts and was marked as resolved."""
  return os.path.exists(_resolved_file(fp))


def _resolved_file(fp):
  fp = os.path.relpath(os.path.abspath(fp), git_common.repo_dir())
  fp = fp.replace(os.path.sep, '-')  # this hack will do the trick for now.
  repo = core.Repository()
  return os.path.join(
      repo.path,
      'GL_RESOLVED_{0}_{1}'.format(repo.current_branch.branch_name, fp))
