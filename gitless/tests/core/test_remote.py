# -*- coding: utf-8 -*-
# Gitless - a version control system built on top of Git.
# Licensed under GNU GPL v2.

"""Unit tests for remote module."""


import tempfile
import os
import shutil

from sh import git

from gitless import core

from . import common


REMOTE_BRANCH = 'rb'


class TestRemote(common.TestCore):
  """Base class for remote tests."""

  def setUp(self):
    """Creates temporary local Git repo to use as the remote."""
    super(TestRemote, self).setUp()

    # Create a repo to use as the remote
    git.config('--global', 'user.name', 'test')
    git.config('--global', 'user.email', 'test@test.com')

    self.remote_path = tempfile.mkdtemp(prefix='gl-remote-test')
    os.chdir(self.remote_path)
    remote_repo = core.init_repository()
    remote_repo.create_branch(
        REMOTE_BRANCH, remote_repo.revparse_single('HEAD'))

    # Go back to the original repo
    os.chdir(self.path)
    self.remotes = self.repo.remotes


  def tearDown(self):
    """Removes the temporary dir."""
    super(TestRemote, self).tearDown()
    shutil.rmtree(self.remote_path)


class TestCreate(TestRemote):

  def test_create_new(self):
    self.remotes.create('remote', self.remote_path)

  def test_create_existing(self):
    self.remotes.create('remote', self.remote_path)
    self.assertRaises(
        ValueError, self.remotes.create, 'remote', self.remote_path)

  def test_create_invalid_name(self):
    self.assertRaises(ValueError, self.remotes.create, 'rem/ote', 'url')

  def test_create_invalid_url(self):
    self.assertRaises(ValueError, self.remotes.create, 'remote', '')


class TestListAll(TestRemote):

  def test_list_all(self):
    self.remotes.create('remote1', self.remote_path)
    self.remotes.create('remote2', self.remote_path)
    self.assertItemsEqual(
        ['remote1', 'remote2'], [r.name for r in self.remotes])


class TestRm(TestRemote):

  def test_rm(self):
    self.remotes.create('remote', self.remote_path)
    self.remotes.delete('remote')

  def test_rm_nonexistent(self):
    self.assertRaises(KeyError, self.remotes.delete, 'remote')
    self.remotes.create('remote', self.remote_path)
    self.remotes.delete('remote')
    self.assertRaises(KeyError, self.remotes.delete, 'remote')


class TestSync(TestRemote):

  def setUp(self):
    super(TestSync, self).setUp()

    with open('foo', 'w') as f:
      f.write('foo')

    git.add('foo')
    git.commit('foo', m='msg')

    self.repo.remotes.create('remote', self.remote_path)
    self.remote = self.repo.remotes['remote']

  def test_sync_changes(self):
    master_head_before = self.remote.lookup_branch('master').head
    remote_branch = self.remote.lookup_branch(REMOTE_BRANCH)
    remote_branch_head_before = remote_branch.head

    current_branch = self.repo.current_branch
    # It is not a ff so it should fail
    self.assertRaises(core.GlError, current_branch.publish, remote_branch)
    # Get the changes
    current_branch.rebase(remote_branch)
    # Retry (this time it should work)
    current_branch.publish(remote_branch)

    self.assertItemsEqual(
        ['master', REMOTE_BRANCH], self.remote.listall_branches())
    self.assertEqual(
        master_head_before.id, self.remote.lookup_branch('master').head.id)

    self.assertNotEqual(
        remote_branch_head_before.id,
        remote_branch.head.id)
    self.assertEqual(current_branch.head.id, remote_branch.head.id)
