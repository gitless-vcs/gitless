# gitpylib - a Python library for Git.
# Licensed under GNU GPL v2.

"""Common methods used accross the gitpylib."""


import os
import shlex
import subprocess
import sys


# Detect if FS is case-sensitive.
import tempfile

tmp_handle, tmp_path = tempfile.mkstemp()
with tempfile.NamedTemporaryFile() as f_tmp:
  FS_CASE_SENSITIVE = not os.path.exists(f_tmp.name.upper())


class UnexpectedOutputError(Exception):

  def __init__(self, cmd, out, err=None):
    super(UnexpectedOutputError, self).__init__()
    self.cmd = cmd
    self.out = out
    self.err = err

  def __str__(self):
    err = 'err was:\n{0}\n' if self.err else ''
    return (
        'Unexpected output from cmd {0}, out was:\n{1}\n{2}'.format(
            self.cmd, self.out, err))


def safe_git_call(cmd):
  ok, out, err = git_call(cmd)
  if ok:
    return out, err
  raise Exception('{0} failed: out is {1}, err is {2}'.format(cmd, out, err))


def git_call(cmd):
  p = subprocess.Popen(
      shlex.split('git {0}'.format(cmd)),
      stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  out, err = p.communicate()
  # Python 2/3 compatibility.
  if sys.version > '3':
    out = out.decode('utf-8')
    err = err.decode('utf-8')
  return p.returncode == 0, out, err


def real_case(fp):
  """Returns the same file path with its real casing.

  Args:
    fp: the file path to get the real-casing for. It should correspond to an
        existing file.

  Returns:
    the same file path with its real casing.
  """
  if FS_CASE_SENSITIVE:
    return fp

  cdir = os.getcwd()
  ret = []
  for p in fp.split('/'):
    found = False
    for f in os.listdir(cdir):
      if f.lower() == p.lower():
        cdir = os.path.join(cdir, p)
        ret.append(f)
        found = True
        break
    if not found:
      # TODO(sperezde): fix this hack (deal with filenames with special
      # characters).
      return fp
  return os.path.join(*ret)


def git_dir():
  """Gets the path to the .git directory

  Returns:
    the absolute path to the git directory or None if the current working
    directory is not a Git repository.
  """
  cd = os.getcwd()
  ret = os.path.join(cd, '.git')
  while cd != '/':  # TODO(sperezde): windows support
    if os.path.isdir(ret):
      return ret
    cd = os.path.dirname(cd)
    ret = os.path.join(cd, '.git')
  return None


def repo_dir():
  """Gets the full path to the Git repo."""
  return git_dir()[:-4]  # Strip "/.git"


def remove_dups(list, key):
  """Returns a new list without duplicates.

  Given two elements e1, e2 from list, e1 is considered to be a duplicate of e2
  if key(e1) == key(e2).

  Args:
    list: the list to read from.
    key: a function that receives an element from list and returns its key.

  Yields:
    unique elements of the given list
  """
  keys = set()
  for a in list:
    k_a = key(a)
    if k_a not in keys:
      keys.add(k_a)
      yield a


def get_all_fps_under_cwd():
  """Returns a list of all existing filepaths under the cwd.

  The filepaths returned are relative to the cwd. The Git directory (.git)
  is ignored.
  """
  for dirpath, dirnames, filenames in os.walk(os.getcwd()):
    if '.git' in dirnames:
      dirnames.remove('.git')
    for fp in filenames:
      yield os.path.relpath(os.path.join(dirpath, fp))


def items(dic):
  """Py 2/3 compatible way of getting the items of a dictionary."""
  try:
    return dic.iteritems()
  except AttributeError:
    return iter(dic.items())
