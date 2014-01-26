# Gitless - a version control system built on top of Git.
# Copyright (c) 2014  Santiago Perez De Rosso.
# Licensed under GNU GPL, version 2.

"""Unit tests for remote module."""


import unittest

from . import common

import gitless.core.remote as remote_lib


class RemoteStub:

  SUCCESS = remote_lib.git_remote.SUCCESS
  REMOTE_NOT_FOUND = remote_lib.git_remote.REMOTE_NOT_FOUND

  def __init__(self):
    self.remotes = {}

  def add(self):
    def stub_add(remote_name, remote_url):
      self.remotes[remote_name] = remote_url
      return self.SUCCESS
    return stub_add

  def show(self):
    def stub_show(remote_name):
      if remote_name not in self.remotes:
        return (self.REMOTE_NOT_FOUND, None)
      return (self.SUCCESS, 'info about {0}'.format(remote_name))
    return stub_show

  def show_all(self):
    def stub_show_all():
      return list(self.remotes.keys())
    return stub_show_all

  def rm(self):
    def stub_rm(remote_name):
      del self.remotes[remote_name]
    return stub_rm


class TestRemote(common.TestCore):
  """Base class for remote tests."""

  def setUp(self):
    super(TestRemote, self).setUp()
    common.stub(remote_lib.git_remote, RemoteStub())


class TestAdd(TestRemote):

  def test_add_new(self):
    self.assertEqual(remote_lib.SUCCESS, remote_lib.add('remote', 'url'))

  def test_add_existing(self):
    remote_lib.add('remote', 'url')
    self.assertEqual(
        remote_lib.REMOTE_ALREADY_SET, remote_lib.add('remote', 'url2'))

  def test_add_invalid_name(self):
    self.assertEqual(remote_lib.INVALID_NAME, remote_lib.add('rem/ote', 'url'))


class TestInfo(TestRemote):

  def test_info_nonexistent(self):
    self.assertEqual(
        remote_lib.REMOTE_NOT_FOUND, remote_lib.info('nonexistent_remote')[0])

  def test_info(self):
    remote_lib.add('remote', 'url')
    self.assertEqual(remote_lib.SUCCESS, remote_lib.info('remote')[0])


class TestInfoAll(TestRemote):

  def test_info_all(self):
    remote_lib.add('remote1', 'url1')
    remote_lib.add('remote2', 'url2')
    self.assertItemsEqual(['remote1', 'remote2'], remote_lib.info_all())


class TestRm(TestRemote):

  def test_rm(self):
    remote_lib.add('remote', 'url')
    self.assertEqual(remote_lib.SUCCESS, remote_lib.rm('remote'))

  def test_rm_nonexistent(self):
    self.assertEqual(remote_lib.REMOTE_NOT_FOUND, remote_lib.rm('remote'))
    remote_lib.add('remote', 'url')
    remote_lib.rm('remote')
    self.assertEqual(remote_lib.REMOTE_NOT_FOUND, remote_lib.rm('remote'))


if __name__ == '__main__':
  unittest.main()
