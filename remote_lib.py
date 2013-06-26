"""Gitless's remote lib."""


from gitpylib import remote


SUCCESS = 1
REMOTE_NOT_FOUND = 2
REMOTE_ALREADY_SET = 3
REMOTE_NOT_FOUND = 4
REMOTE_UNREACHABLE = 5


def add(remote_name, remote_url):
  """Add a remote for the current Gitless repo.
  
  Args:
    remote_name: the name of the remote.
    remote_url: the url of the remote

  Returns:
    REMOTE_ALREADY_SET, REMOTE_UNREACHABLE or SUCCESS.
  """
  if is_set(remote_name):
    return (REMOTE_ALREADY_SET, None)
  remote.add(remote_name, remote_url)
  ret, out = info(remote_name)
  if ret is REMOTE_UNREACHABLE:
    remote.rm(remote_name)
    return (REMOTE_UNREACHABLE, None)
  return (SUCCESS, out)


def is_set(remote_name):
  return remote_name in remote.list()


def info(remote_name):
  ret, info = remote.show(remote_name)
  if ret is remote.REMOTE_NOT_FOUND:
    return (REMOTE_NOT_FOUND, None)
  elif ret is remote.REMOTE_UNREACHABLE:
    return (REMOTE_UNREACHABLE, None)
  elif ret is remote.SUCCESS:
    return (SUCCESS, info)


def list():
  return remote.list()


def rm(remote_name):
  if not is_set(remote_name):
    return REMOTE_NOT_FOUND
  remote.rm(remote_name)
  return SUCCESS
