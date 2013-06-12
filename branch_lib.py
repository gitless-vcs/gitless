"""Gitless's branching lib."""


from gitpylib import branch
from gitpylib import stash


def create(name):
  """Creates a new branch with the given name.

  Args:
    name: the name of the branch to create.
  """
  branch.create(name)


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
  stash.all('---gl-%s---' % branch.current())
  branch.checkout(name)
  stash.pop('---gl-%s---' % name)


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


def status_all():
  """Get the status of all existing branches.
  
  Yields:
    Tuples of the form (name, is_current, tracks) where is_current is a boolean
    value and tracks is a string representing the remote branch it tracks (in 
    the format 'remote_name/remote_branch') or None if it is a local branch.
  """
  return branch.status_all()
