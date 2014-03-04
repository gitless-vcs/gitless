# Gitless - a version control system built on top of Git.
# Copyright (c) 2014  Santiago Perez De Rosso.
# Licensed under GNU GPL, version 2.

"""Unit tests for remote module."""


import unittest

from . import common
from . import stubs

import gitless.core.remote as remote_lib



class TestRemote(common.TestCore):
  """Base class for remote tests."""

  def setUp(self):
    super(TestRemote, self).setUp()
    # Re-stub the module with a fresh RemoteLib instance.
    # This keeps unit tests independent between each other.
    common.stub(remote_lib.git_remote, stubs.RemoteLib())


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
    self.assertItemsEqual(
        [remote_lib.RemoteInfo('remote1', 'url1', 'url1'),
         remote_lib.RemoteInfo('remote2', 'url2', 'url2')],
        remote_lib.info_all())


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
