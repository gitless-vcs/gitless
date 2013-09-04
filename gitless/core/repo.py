# Gitless - a version control system built on top of Git.
# Copyright (c) 2013  Santiago Perez De Rosso.
# Licensed under GNU GPL, version 2.

"""Gitless's repo lib."""


import os

from gitpylib import common as git_common
from gitpylib import config as git_config
from gitpylib import file as git_file
from gitpylib import status as git_status
from gitpylib import repo as git_repo


SUCCESS = 1
NOTHING_TO_INIT = 2


def cwd():
  """Gets the Gitless's cwd."""
  dr = os.path.dirname(gl_dir())
  cwd = os.getcwd()
  return '/' if dr == cwd else cwd[len(dr):]


def gl_dir():
  """Gets the path to the gl directory.

  Returns:
    The absolute path to the gl directory or None if the current working
    directory is not a Gitless repository.
  """
  # We use the same .git directory.
  return git_common.git_dir()


def status():
  """Gets the status of the repo.

  Returns:
      A pair (tracked_mod_list, untracked_list) where
      - tracked_mod_list: contains a tuple (fp, exists_in_lr, exists_in_wd,
        in_conflict)
      - untracked_list: contains a pair (fp, exists_in_lr, exists_in_wd).
  """
  # TODO(sperezde): Will probably need to implement this smarter in the future.
  # TODO(sperezde): using frozenset should improve performance.
  tracked_mod_list = []
  untracked_list = []
  for (s, fp) in git_status.of_repo():
    if s is git_status.TRACKED_UNMODIFIED:
      # We don't return tracked unmodified files.
      continue

    if s is git_status.TRACKED_MODIFIED:
      tracked_mod_list.append((fp, True, True, False))
    elif s is git_status.STAGED:
      tracked_mod_list.append((fp, False, True, False))
    elif s is git_status.ASSUME_UNCHANGED:
      untracked_list.append((fp, True, True))
    elif s is git_status.DELETED:
      tracked_mod_list.append((fp, True, False, False))
    elif s is git_status.DELETED_STAGED:
      git_file.unstage(fp)
    elif s is git_status.DELETED_ASSUME_UNCHANGED:
      untracked_list.append((fp, True, False))
    elif s is git_status.IN_CONFLICT:
      tracked_mod_list.append((fp, True, True, True))
    elif s is git_status.IGNORED or s is git_status.IGNORED_STAGED:
      # We don't return ignored files.
      pass
    elif s is git_status.MODIFIED_MODIFIED:
      # The file was marked as resolved and then modified. To Gitless, this is
      # just a regular tracked file.
      tracked_mod_list.append((fp, True, True, False))
    elif s is git_status.ADDED_MODIFIED:
      # The file is a new file that was added and then modified. This can only
      # happen if the user gl tracks a file and then modifies it.
      tracked_mod_list.append((fp, False, True, False))
    else:
      untracked_list.append((fp, False, True))

  return (tracked_mod_list, untracked_list)


def init_from(remote_repo):
  if gl_dir():
    return NOTHING_TO_INIT
  git_repo.clone(remote_repo)
  return SUCCESS


def init_dir():
  if gl_dir():
    return NOTHING_TO_INIT
  git_repo.init()
  return SUCCESS


def editor():
  """Returns the editor set up by the user (defaults to Vim)."""
  ret = git_config.get('core.editor')
  if ret:
    return ret
  # We check the $EDITOR variable.
  ret = os.environ['EDITOR'] if 'EDITOR' in os.environ else None
  if ret:
    return ret
  # We default to Vim.
  return 'vim'
