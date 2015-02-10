# gitpylib - a Python library for Git.
# Licensed under GNU GPL v2.

"""Module for getting the status of the repo."""


import os

from . import common
from . import config


def of_file(fp):
  """Gets the status of the given file.

  Args:
    fp: the path of the file to status (e.g., 'paper.tex').

  Returns:
    None if the given file doesn't exist or one of the possible status codes.
  """
  return next(of(only_paths=[fp]), (None, None))[1]


def of(only_paths=None, relative_paths=None):
  """Status of the repo or of the only_paths given.

  Returns:
    A list of (fp, status) pairs. fp is a file path and status is a two or three
    letter code corresponding to the output from status porcelain and ls-files
    (see git manual for more info).
  """
  if not relative_paths:
    c = config.get('status.relativePaths')
    relative_paths = c if c else True  # git seems to default to true

  if only_paths:
    pathspecs = '"' + '" "'.join(only_paths) + '"'
  else:
    pathspecs = common.repo_dir()

  ret = {}
  repo_dir = common.repo_dir()

  def status_porcelain():
    out, _ = common.safe_git_call(
        'status --porcelain -u --ignored {0}'.format(pathspecs))
    for f_out in out.splitlines():
      # Output is in the form <status> <file path>.
      # <status> is 2 chars long.
      fp, s = f_out[3:], f_out[:2]
      if fp.startswith('"'):
        fp = fp[1:-1]
      if relative_paths:
        fp = os.path.relpath(os.path.join(repo_dir, fp))
      ret[fp] = s

  def ls_files():
    out, _ = common.safe_git_call(
        'ls-files -v --full-name -- {0}'.format(pathspecs))
    for f_out in common.remove_dups(out.splitlines(), lambda x: x[2:]):
      fp, s = f_out[2:], f_out[0]
      if relative_paths:
        fp = os.path.relpath(os.path.join(repo_dir, fp))
      if fp in ret:
        ret[fp] = ret[fp] + s
      else:
        ret[fp] = '  ' + s

  status_porcelain()
  ls_files()
  return common.items(ret)


def au_files():
  """Assumed unchanged files."""
  out, _ = common.safe_git_call('ls-files -v --full-name')
  for f_out in common.remove_dups(out.splitlines(), lambda x: x[2:]):
    if f_out[0] == 'h':
      yield f_out[2:]
