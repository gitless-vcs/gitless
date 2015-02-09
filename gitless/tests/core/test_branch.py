# Gitless - a version control system built on top of Git.
# Licensed under GNU GPL v2.

"""Unit tests for branch module."""


import os

import gitless.core.branch as branch_lib
import gitless.core.file as file_lib
import gitless.core.remote as remote_lib
import gitless.core.sync as sync_lib
import gitless.tests.utils as utils_lib

from . import common
from . import stubs


TRACKED_FP = 'f1'
TRACKED_FP_CONTENTS_1 = 'f1-1'
TRACKED_FP_CONTENTS_2 = 'f1-2'
UNTRACKED_FP = 'f2'
UNTRACKED_FP_CONTENTS = 'f2'
IGNORED_FP = 'f3'
BRANCH = 'b1'


class TestBranch(common.TestCore):
  """Base class for branch tests."""

  def setUp(self):
    super(TestBranch, self).setUp()

    # Build up an interesting mock repo.
    utils_lib.write_file(TRACKED_FP, contents=TRACKED_FP_CONTENTS_1)
    utils_lib.git_call('add "{0}"'.format(TRACKED_FP))
    utils_lib.git_call('commit -m"1" "{0}"'.format(TRACKED_FP))
    utils_lib.write_file(TRACKED_FP, contents=TRACKED_FP_CONTENTS_2)
    utils_lib.git_call('commit -m"2" "{0}"'.format(TRACKED_FP))
    utils_lib.write_file(UNTRACKED_FP, contents=UNTRACKED_FP_CONTENTS)
    utils_lib.write_file('.gitignore', contents='{0}'.format(IGNORED_FP))
    utils_lib.write_file(IGNORED_FP)
    utils_lib.git_call('branch "{0}"'.format(BRANCH))


class TestCreate(TestBranch):

  def test_create_invalid_name(self):
    self.assertEqual(branch_lib.INVALID_NAME, branch_lib.create('evil/branch'))
    self.assertEqual(branch_lib.INVALID_NAME, branch_lib.create('evil_branch'))
    self.assertEqual(branch_lib.INVALID_NAME, branch_lib.create(''))
    self.assertEqual(branch_lib.INVALID_NAME, branch_lib.create('\t'))
    self.assertEqual(branch_lib.INVALID_NAME, branch_lib.create('   '))

  def test_create_existent_name(self):
    self.assertEqual(branch_lib.SUCCESS, branch_lib.create('branch1'))
    self.assertEqual(
        branch_lib.BRANCH_ALREADY_EXISTS, branch_lib.create('branch1'))

  def test_create(self):
    self.assertEqual(branch_lib.SUCCESS, branch_lib.create('branch1'))
    self.assertEqual(branch_lib.SUCCESS, branch_lib.switch('branch1'))
    self.assertTrue(os.path.exists(TRACKED_FP))
    self.assertEqual(TRACKED_FP_CONTENTS_2, utils_lib.read_file(TRACKED_FP))
    self.assertFalse(os.path.exists(UNTRACKED_FP))
    self.assertFalse(os.path.exists(IGNORED_FP))
    self.assertFalse(os.path.exists('.gitignore'))

  def test_create_from_prev_commit(self):
    self.assertEqual(
        branch_lib.SUCCESS, branch_lib.create('branch1', dp='HEAD^'))
    self.assertEqual(branch_lib.SUCCESS, branch_lib.switch('branch1'))
    self.assertTrue(os.path.exists(TRACKED_FP))
    self.assertEqual(TRACKED_FP_CONTENTS_1, utils_lib.read_file(TRACKED_FP))
    self.assertFalse(os.path.exists(UNTRACKED_FP))
    self.assertFalse(os.path.exists(IGNORED_FP))
    self.assertFalse(os.path.exists('.gitignore'))


class TestDelete(TestBranch):

  def test_delete_nonexistent_branch(self):
    self.assertEqual(
        branch_lib.NONEXISTENT_BRANCH, branch_lib.delete('nonexistent'))

  def test_delete(self):
    self.assertEqual(
        branch_lib.SUCCESS, branch_lib.delete(BRANCH))


class TestSwitch(TestBranch):

  def test_switch_contents_still_there_untrack_tracked(self):
    file_lib.untrack(TRACKED_FP)
    utils_lib.write_file(TRACKED_FP, contents='contents')
    self.assertEqual(branch_lib.SUCCESS, branch_lib.switch(BRANCH))
    self.assertEqual(TRACKED_FP_CONTENTS_2, utils_lib.read_file(TRACKED_FP))
    self.assertEqual(branch_lib.SUCCESS, branch_lib.switch('master'))
    self.assertEqual('contents', utils_lib.read_file(TRACKED_FP))

  def test_switch_contents_still_there_untracked(self):
    self.assertEqual(branch_lib.SUCCESS, branch_lib.switch(BRANCH))
    utils_lib.write_file(UNTRACKED_FP, contents='contents')
    self.assertEqual(branch_lib.SUCCESS, branch_lib.switch('master'))
    self.assertEqual(UNTRACKED_FP_CONTENTS, utils_lib.read_file(UNTRACKED_FP))
    self.assertEqual(branch_lib.SUCCESS, branch_lib.switch(BRANCH))
    self.assertEqual('contents', utils_lib.read_file(UNTRACKED_FP))

  def test_switch_contents_still_there_ignored(self):
    self.assertEqual(branch_lib.SUCCESS, branch_lib.switch(BRANCH))
    utils_lib.write_file(IGNORED_FP, contents='contents')
    self.assertEqual(branch_lib.SUCCESS, branch_lib.switch('master'))
    self.assertEqual(IGNORED_FP, utils_lib.read_file(IGNORED_FP))
    self.assertEqual(branch_lib.SUCCESS, branch_lib.switch(BRANCH))
    self.assertEqual('contents', utils_lib.read_file(IGNORED_FP))

  def test_switch_contents_still_there_tracked_commit(self):
    utils_lib.write_file(TRACKED_FP, contents='commit')
    utils_lib.git_call('commit -m\'comment\' {0}'.format(TRACKED_FP))
    self.assertEqual(branch_lib.SUCCESS, branch_lib.switch(BRANCH))
    self.assertEqual(TRACKED_FP_CONTENTS_2, utils_lib.read_file(TRACKED_FP))
    self.assertEqual(branch_lib.SUCCESS, branch_lib.switch('master'))
    self.assertEqual('commit', utils_lib.read_file(TRACKED_FP))

  def test_switch_file_classification_is_mantained(self):
    file_lib.untrack(TRACKED_FP)
    self.assertEqual(branch_lib.SUCCESS, branch_lib.switch(BRANCH))
    st = file_lib.status(TRACKED_FP)
    self.assertTrue(st)
    self.assertEqual(file_lib.TRACKED, st.type)
    self.assertEqual(branch_lib.SUCCESS, branch_lib.switch('master'))
    st = file_lib.status(TRACKED_FP)
    self.assertTrue(st)
    self.assertEqual(file_lib.UNTRACKED, st.type)

  def test_switch_with_hidden_files(self):
    hf = '.file'
    utils_lib.write_file(hf)
    self.assertEqual(branch_lib.SUCCESS, branch_lib.switch(BRANCH))
    utils_lib.write_file(hf, contents='contents')
    self.assertEqual(branch_lib.SUCCESS, branch_lib.switch('master'))
    self.assertEqual(hf, utils_lib.read_file(hf))
    self.assertEqual(branch_lib.SUCCESS, branch_lib.switch(BRANCH))
    self.assertEqual('contents', utils_lib.read_file(hf))


class TestUpstream(TestBranch):

  REMOTE_NAME = 'remote'
  REMOTE_URL = 'url'

  def setUp(self):
    super(TestUpstream, self).setUp()
    common.stub(remote_lib.git_remote, stubs.RemoteLib())
    remote_lib.add(self.REMOTE_NAME, self.REMOTE_URL)

  def test_set_upstream_no_remote(self):
    self.assertEqual(
        branch_lib.REMOTE_NOT_FOUND, branch_lib.set_upstream('r/b'))

  def test_set_upstream(self):
    self.assertEqual(
        branch_lib.SUCCESS,
        branch_lib.set_upstream(self.REMOTE_NAME + '/branch'))

  def test_unset_upstream_no_upstream(self):
    self.assertEqual(
        branch_lib.UPSTREAM_NOT_SET, branch_lib.unset_upstream())

  def test_unset_upstream(self):
    remote_branch = self.REMOTE_NAME + '/branch'
    status = lambda name: branch_lib.git_branch.BranchStatus(
        name, True, remote_branch)
    with common.stub(
        branch_lib.git_branch,
        {'status': status,
         'set_upstream': lambda *_: branch_lib.git_branch.SUCCESS,
         'unset_upstream': lambda _: branch_lib.git_branch.SUCCESS}):
      branch_lib.set_upstream(remote_branch)
      self.assertEqual(branch_lib.SUCCESS, branch_lib.unset_upstream())

  def test_publish_nonexistent_upstream(self):
    def on_push(b, rn, rb):
      self.assertEqual(rb, 'branch-branch')
      return sync_lib.git_sync.SUCCESS, ''
    remote_branch = self.REMOTE_NAME + '/branch-branch'
    status = lambda name: branch_lib.git_branch.BranchStatus(name, False, None)
    with common.stub(
        branch_lib.git_branch,
        {'status': status,
         'set_upstream': lambda *_: branch_lib.git_branch.UNFETCHED_OBJECT}):
      with common.stub(branch_lib.remote_lib, {'is_set': lambda _: True}):
        branch_lib.set_upstream(remote_branch)
        with common.stub(sync_lib.git_sync, {'push': on_push}):
          self.assertEqual(branch_lib.SUCCESS, sync_lib.publish()[0])
