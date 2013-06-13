"""Gitless's branching lib."""


from gitpylib import branch
from gitpylib import stash


def create(name):
  """Creates a new branch with the given name.

  Args:
    name: the name of the branch to create.
  """
  branch.create(name)


def delete(name):
  """Deletes the branch with the given name.

  Args:
    name: the name of the branch to delete.
  """
  branch.force_delete(name)
  # We also cleanup any stash left.
  stash.drop(_stash_msg(name))


def attach(name, remote):
  """Attaches the branch with the given name to remote.

  Args:
    name: the name of the branch to attach to the remote.
    remote: the remote branch.
  """
  # TBD


def detach(name):
  """Detaches the branch with the given name from its remote.

  Args:
    name: the name of the branch to detach.
  """
  # TBD


def switch(name):
  """Switches to the branch with the given name.

  Args:
    name: the name of the destination branch.
  """
  stash.all(_stash_msg(current()))
  branch.checkout(name)
  stash.pop(_stash_msg(name))


def status(name):
  """Get the status of the branch with the given name.

  Args:
    name: the name of the branch to status.
  
  Returns:
    A tuple (exists, is_current, tracks) where exists and is_current are boolean
    values and tracks is a string representing the remote branch it tracks (in
    the format 'remote_name/remote_branch') or None if it is a local branch.
  """
  return branch.status(name)


def current():
  """Get the name of the current branch."""
  return branch.current()


def status_all():
  """Get the status of all existing branches.
  
  Yields:
    Tuples of the form (name, is_current, tracks) where is_current is a boolean
    value and tracks is a string representing the remote branch it tracks (in 
    the format 'remote_name/remote_branch') or None if it is a local branch.
  """
  return branch.status_all()


def _stash_msg(name):
  """Computes the stash msg to use for stashin changes in branch name."""
  return '---gl-%s---' % name
