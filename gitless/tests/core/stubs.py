# Gitless - a version control system built on top of Git.
# Licensed under GNU GPL v2.

"""Stubs."""


from gitless.gitpylib import remote as git_remote


class RemoteLib(object):

  SUCCESS = git_remote.SUCCESS
  REMOTE_NOT_FOUND = git_remote.REMOTE_NOT_FOUND

  def __init__(self):
    self.remotes = {}

  def add(self, remote_name, remote_url):
    self.remotes[remote_name] = remote_url
    return self.SUCCESS

  def show(self, remote_name):
    if remote_name not in self.remotes:
      return self.REMOTE_NOT_FOUND, None
    return self.SUCCESS, 'info about {0}'.format(remote_name)

  def show_all(self):
    return list(self.remotes.keys())

  def show_all_v(self):
    ret = []
    for rn, ru in self.remotes.items():
      ret.append(git_remote.RemoteInfo(rn, ru, ru))
    return ret

  def rm(self, remote_name):
    del self.remotes[remote_name]
