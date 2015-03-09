# gitpylib - a Python library for Git.
# Licensed under GNU GPL v2.

"""Common methods used accross the gitpylib."""


import os
import shlex
import subprocess
import sys


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


def items(dic):
  """Py 2/3 compatible way of getting the items of a dictionary."""
  try:
    return dic.iteritems()
  except AttributeError:
    return iter(dic.items())
