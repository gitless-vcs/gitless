# Gitless - a version control system built on top of Git.
# Licensed under GNU GPL v2.

"""Unit tests for branch related operations."""


import os

import gitless.core.core as core
import gitless.core.file as file_lib
import gitless.tests.utils as utils_lib

from . import common


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

  def _assert_value_error(self, name, regexp):
    self.assertRaisesRegexp(
        ValueError, regexp, self.repo.create_branch, name,
        self.repo.current_branch.head)

  def test_create_invalid_name(self):
    assert_invalid_name = lambda n: self._assert_value_error(n, 'not valid')
    assert_invalid_name('')
    assert_invalid_name('\t')
    assert_invalid_name('  ')

  def test_create_existent_name(self):
    self.repo.create_branch('branch1', self.repo.current_branch.head)
    self._assert_value_error('branch1', 'exists')

  def test_create(self):
    self.repo.create_branch('branch1', self.repo.current_branch.head)
    self.repo.switch_current_branch(self.repo.lookup_branch('branch1'))
    self.assertTrue(os.path.exists(TRACKED_FP))
    self.assertEqual(TRACKED_FP_CONTENTS_2, utils_lib.read_file(TRACKED_FP))
    self.assertFalse(os.path.exists(UNTRACKED_FP))
    self.assertFalse(os.path.exists(IGNORED_FP))
    self.assertFalse(os.path.exists('.gitignore'))

  def test_create_from_prev_commit(self):
    self.repo.create_branch('branch1', self.repo.revparse_single('HEAD^'))
    self.repo.switch_current_branch(self.repo.lookup_branch('branch1'))
    self.assertTrue(os.path.exists(TRACKED_FP))
    self.assertEqual(TRACKED_FP_CONTENTS_1, utils_lib.read_file(TRACKED_FP))
    self.assertFalse(os.path.exists(UNTRACKED_FP))
    self.assertFalse(os.path.exists(IGNORED_FP))
    self.assertFalse(os.path.exists('.gitignore'))


class TestDelete(TestBranch):

  def test_delete(self):
    self.repo.lookup_branch(BRANCH).delete()
    self.assertRaises(
        core.BranchIsCurrentError,
        self.repo.lookup_branch('master').delete)


class TestSwitch(TestBranch):

  def test_switch_contents_still_there_untrack_tracked(self):
    file_lib.untrack(TRACKED_FP)
    utils_lib.write_file(TRACKED_FP, contents='contents')
    self.repo.switch_current_branch(self.repo.lookup_branch(BRANCH))
    self.assertEqual(TRACKED_FP_CONTENTS_2, utils_lib.read_file(TRACKED_FP))
    self.repo.switch_current_branch(self.repo.lookup_branch('master'))
    self.assertEqual('contents', utils_lib.read_file(TRACKED_FP))

  def test_switch_contents_still_there_untracked(self):
    self.repo.switch_current_branch(self.repo.lookup_branch(BRANCH))
    utils_lib.write_file(UNTRACKED_FP, contents='contents')
    self.repo.switch_current_branch(self.repo.lookup_branch('master'))
    self.assertEqual(UNTRACKED_FP_CONTENTS, utils_lib.read_file(UNTRACKED_FP))
    self.repo.switch_current_branch(self.repo.lookup_branch(BRANCH))
    self.assertEqual('contents', utils_lib.read_file(UNTRACKED_FP))

  def test_switch_contents_still_there_ignored(self):
    self.repo.switch_current_branch(self.repo.lookup_branch(BRANCH))
    utils_lib.write_file(IGNORED_FP, contents='contents')
    self.repo.switch_current_branch(self.repo.lookup_branch('master'))
    self.assertEqual(IGNORED_FP, utils_lib.read_file(IGNORED_FP))
    self.repo.switch_current_branch(self.repo.lookup_branch(BRANCH))
    self.assertEqual('contents', utils_lib.read_file(IGNORED_FP))

  def test_switch_contents_still_there_tracked_commit(self):
    utils_lib.write_file(TRACKED_FP, contents='commit')
    utils_lib.git_call('commit -m\'comment\' {0}'.format(TRACKED_FP))
    self.repo.switch_current_branch(self.repo.lookup_branch(BRANCH))
    self.assertEqual(TRACKED_FP_CONTENTS_2, utils_lib.read_file(TRACKED_FP))
    self.repo.switch_current_branch(self.repo.lookup_branch('master'))
    self.assertEqual('commit', utils_lib.read_file(TRACKED_FP))

  def test_switch_file_classification_is_mantained(self):
    file_lib.untrack(TRACKED_FP)
    self.repo.switch_current_branch(self.repo.lookup_branch(BRANCH))
    st = file_lib.status(TRACKED_FP)
    self.assertTrue(st)
    self.assertEqual(file_lib.TRACKED, st.type)
    self.repo.switch_current_branch(self.repo.lookup_branch('master'))
    st = file_lib.status(TRACKED_FP)
    self.assertTrue(st)
    self.assertEqual(file_lib.UNTRACKED, st.type)

  def test_switch_with_hidden_files(self):
    hf = '.file'
    utils_lib.write_file(hf)
    self.repo.switch_current_branch(self.repo.lookup_branch(BRANCH))
    utils_lib.write_file(hf, contents='contents')
    self.repo.switch_current_branch(self.repo.lookup_branch('master'))
    self.assertEqual(hf, utils_lib.read_file(hf))
    self.repo.switch_current_branch(self.repo.lookup_branch(BRANCH))
    self.assertEqual('contents', utils_lib.read_file(hf))
