# Gitless - a version control system built on top of Git.
# Licensed under GNU GPL v2.

"""Gitless's repo lib."""


import os


from gitless.gitpylib import config as git_config
from gitless.gitpylib import log as git_log


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
