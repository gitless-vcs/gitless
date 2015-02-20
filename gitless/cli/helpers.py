# Gitless - a version control system built on top of Git.
# Licensed under GNU GPL v2.

"""Some helpers for commands."""


def get_branch_name(branch):
  try:
    return branch.remote_name + '/' + branch.branch_name
  except AttributeError:
    return branch.branch_name


def get_branch(branch_name, repo):
  b = None
  if '/' not in branch_name:
    # It is a local branch
    b = repo.lookup_branch(branch_name)
    if not b:
      raise ValueError('Branch "{0}" doesn\'t exist'.format(branch_name))
  else:
    # It is a remote branch
    remote, remote_branch = branch_name.split('/', 1)
    try:
      r = repo.remotes[remote]
    except KeyError:
      raise ValueError('Remote "{0}" doesn\'t exist'.format(remote))

    b = r.lookup_branch(remote_branch)
    if not b:
      raise ValueError('Branch "{0}" doesn\'t exist in remote "{1}"'.format(
          remote_branch, remote))
  return b
