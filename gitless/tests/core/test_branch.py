# Gitless - a version control system built on top of Git.
# Copyright (c) 2013  Santiago Perez De Rosso.
# Licensed under GNU GPL, version 2.

"""Unit tests for branch module."""


import os
import unittest

import gitless.core.branch as branch_lib
import common


TRACKED_FP = 'f1'
TRACKED_FP_CONTENTS_1 = 'f1-1'
TRACKED_FP_CONTENTS_2 = 'f1-2'
UNTRACKED_FP = 'f2'
IGNORED_FP = 'f3'


class TestBranch(common.TestCore):
  """Base class for branch tests."""

  def setUp(self):
    super(TestBranch, self).setUp()

    # Build up an interesting mock repo.
    self._git_call('init')
    self._write_file(TRACKED_FP, contents=TRACKED_FP_CONTENTS_1)
    self._git_call('add "{}"'.format(TRACKED_FP))
    self._git_call('commit -m"1" "{}"'.format(TRACKED_FP))
    self._write_file(TRACKED_FP, contents=TRACKED_FP_CONTENTS_2)
    self._git_call('commit -m"2" "{}"'.format(TRACKED_FP))
    self._write_file(UNTRACKED_FP)
    self._write_file('.gitignore', contents='{}'.format(IGNORED_FP))
    self._write_file(IGNORED_FP)


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
    self.assertEqual(TRACKED_FP_CONTENTS_2, self._read_file(TRACKED_FP))
    self.assertFalse(os.path.exists(UNTRACKED_FP))
    self.assertFalse(os.path.exists(IGNORED_FP))
    self.assertFalse(os.path.exists('.gitignore'))

  def test_create_from_prev_commit(self):
    self.assertEqual(
        branch_lib.SUCCESS, branch_lib.create('branch1', dp='HEAD^'))
    self.assertEqual(branch_lib.SUCCESS, branch_lib.switch('branch1'))
    self.assertTrue(os.path.exists(TRACKED_FP))
    self.assertEqual(TRACKED_FP_CONTENTS_1, self._read_file(TRACKED_FP))
    self.assertFalse(os.path.exists(UNTRACKED_FP))
    self.assertFalse(os.path.exists(IGNORED_FP))
    self.assertFalse(os.path.exists('.gitignore'))


class TestDelete(TestBranch):

  def test_delete_nonexistent_branch(self):
    self.assertEqual(
        branch_lib.NONEXISTENT_BRANCH, branch_lib.delete('nonexistent'))


if __name__ == '__main__':
  unittest.main()
