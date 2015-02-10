# gitpylib - a Python library for Git.
# Licensed under GNU GPL v2.


from . import common


def clone(repo):
  """Returns True if the clone succeeded, False if otherwise."""
  return common.git_call('clone {0} .'.format(repo))[0]


def init():
  common.safe_git_call('init')
