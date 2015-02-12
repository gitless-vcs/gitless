# Gitless - a version control system built on top of Git.
# Licensed under GNU GPL v2.

"""Gitless's repo lib."""


import os

import pygit2

from gitless.gitpylib import config as git_config
from gitless.gitpylib import log as git_log


class GlError(Exception):
  pass

class NotInRepoError(GlError):

  def __init__(self):
    super(NotInRepoError, self).__init__('You are not in a Gitless repository')


def cwd():
  """Gets the Gitless's cwd."""
  dr = os.path.dirname(gl_dir())
  cwd = os.getcwd()
  return '/' if dr == cwd else cwd[len(dr):]


def gl_dir():
  """Gets the path to the gl directory.

  Returns:
    the absolute path to the gl directory.
  """
  # We use the same .git directory.
  try:
    # The path is returned with a trailing '/'
    return pygit2.discover_repository(os.getcwd())[:-1]
  except Exception:
    raise NotInRepoError()


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


def color_output():
  ret = git_config.get('color.ui')
  if ret and ret.lower() in ['true', 'always']:
    return True
  return False


def history(include_diffs=False):
  return git_log.log(include_diffs=include_diffs)
