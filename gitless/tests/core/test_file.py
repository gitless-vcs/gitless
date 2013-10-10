# Gitless - a version control system built on top of Git.
# Copyright (c) 2013  Santiago Perez De Rosso.
# Licensed under GNU GPL, version 2.

"""Unit tests for file module."""


import unittest

import gitless.core.file as file_lib
import common


TRACKED_FP = 'f1'
TRACKED_FP_CONTENTS_1 = 'f1-1'
TRACKED_FP_CONTENTS_2 = 'f1-2'
TRACKED_FP_WITH_SPACE = 'f1 space'
UNTRACKED_FP = 'f2'
UNTRACKED_FP_WITH_SPACE = 'f2 space'
IGNORED_FP = 'f3'
IGNORED_FP_WITH_SPACE = 'f3 space'
NONEXISTENT_FP = 'nonexistent'
NONEXISTENT_FP_WITH_SPACE = 'nonexistent'


class TestFile(common.TestCore):
  """Base class for file tests."""

  def setUp(self):
    super(TestFile, self).setUp()

    # Build up an interesting mock repo.
    self._git_call('init')
    self._write_file(TRACKED_FP, contents=TRACKED_FP_CONTENTS_1)
    self._write_file(TRACKED_FP_WITH_SPACE, contents=TRACKED_FP_CONTENTS_1)
    self._git_call('add "{}" "{}"'.format(TRACKED_FP, TRACKED_FP_WITH_SPACE))
    self._git_call(
        'commit -m"1" "{}" "{}"'.format(TRACKED_FP, TRACKED_FP_WITH_SPACE))
    self._write_file(TRACKED_FP, contents=TRACKED_FP_CONTENTS_2)
    self._write_file(TRACKED_FP_WITH_SPACE, contents=TRACKED_FP_CONTENTS_2)
    self._git_call(
        'commit -m"2" "{}" "{}"'.format(TRACKED_FP, TRACKED_FP_WITH_SPACE))
    self._write_file(UNTRACKED_FP)
    self._write_file(UNTRACKED_FP_WITH_SPACE)
    self._write_file(
      '.gitignore', contents='{}\n{}'.format(IGNORED_FP, IGNORED_FP_WITH_SPACE))
    self._write_file(IGNORED_FP)
    self._write_file(IGNORED_FP_WITH_SPACE)


class TestTrackFile(TestFile):

  @common.assert_contents_unchanged(UNTRACKED_FP)
  def test_track_untracked_fp(self):
    self.assertEqual(file_lib.SUCCESS, file_lib.track(UNTRACKED_FP))
    self.assertEqual(file_lib.TRACKED, file_lib.status(UNTRACKED_FP).type)

  @common.assert_contents_unchanged(UNTRACKED_FP_WITH_SPACE)
  def test_track_untracked_fp_with_space(self):
    self.assertEqual(file_lib.SUCCESS, file_lib.track(UNTRACKED_FP_WITH_SPACE))
    self.assertEqual(
      file_lib.TRACKED, file_lib.status(UNTRACKED_FP_WITH_SPACE).type)

  @common.assert_no_side_effects(TRACKED_FP)
  def test_track_tracked_fp(self):
    self.assertEqual(file_lib.FILE_ALREADY_TRACKED, file_lib.track(TRACKED_FP))

  @common.assert_no_side_effects(TRACKED_FP_WITH_SPACE)
  def test_track_tracked_fp_with_space(self):
    self.assertEqual(
      file_lib.FILE_ALREADY_TRACKED, file_lib.track(TRACKED_FP_WITH_SPACE))

  def test_track_nonexistent_fp(self):
    self.assertEqual(file_lib.FILE_NOT_FOUND, file_lib.track(NONEXISTENT_FP))

  def test_track_nonexistent_fp_with_space(self):
    self.assertEqual(
      file_lib.FILE_NOT_FOUND, file_lib.track(NONEXISTENT_FP_WITH_SPACE))

  @common.assert_no_side_effects(IGNORED_FP)
  def test_track_ignored(self):
    self.assertEqual(file_lib.FILE_IS_IGNORED, file_lib.track(IGNORED_FP))

  @common.assert_no_side_effects(IGNORED_FP_WITH_SPACE)
  def test_track_ignored_with_space(self):
    self.assertEqual(
      file_lib.FILE_IS_IGNORED, file_lib.track(IGNORED_FP_WITH_SPACE))


class TestUntrackFile(TestFile):

  @common.assert_contents_unchanged(TRACKED_FP)
  def test_untrack_tracked_fp(self):
    self.assertEqual(file_lib.SUCCESS, file_lib.untrack(TRACKED_FP))
    self.assertEqual(file_lib.UNTRACKED, file_lib.status(TRACKED_FP).type)

  @common.assert_contents_unchanged(TRACKED_FP_WITH_SPACE)
  def test_untrack_tracked_fp_space(self):
    self.assertEqual(file_lib.SUCCESS, file_lib.untrack(TRACKED_FP_WITH_SPACE))
    self.assertEqual(
        file_lib.UNTRACKED, file_lib.status(TRACKED_FP_WITH_SPACE).type)

  @common.assert_no_side_effects(UNTRACKED_FP)
  def test_untrack_untracked_fp(self):
    self.assertEqual(
        file_lib.FILE_ALREADY_UNTRACKED, file_lib.untrack(UNTRACKED_FP))

  @common.assert_no_side_effects(UNTRACKED_FP_WITH_SPACE)
  def test_untrack_untracked_fp_with_space(self):
    self.assertEqual(
        file_lib.FILE_ALREADY_UNTRACKED,
        file_lib.untrack(UNTRACKED_FP_WITH_SPACE))

  def test_untrack_nonexistent_fp(self):
    self.assertEqual(file_lib.FILE_NOT_FOUND, file_lib.untrack(NONEXISTENT_FP))

  def test_untrack_nonexistent_fp_with_space(self):
    self.assertEqual(
        file_lib.FILE_NOT_FOUND, file_lib.untrack(NONEXISTENT_FP_WITH_SPACE))

  @common.assert_no_side_effects(IGNORED_FP)
  def test_untrack_ignored(self):
    self.assertEqual(file_lib.FILE_IS_IGNORED, file_lib.untrack(IGNORED_FP))

  @common.assert_no_side_effects(IGNORED_FP_WITH_SPACE)
  def test_untrack_ignored_with_space(self):
    self.assertEqual(
        file_lib.FILE_IS_IGNORED, file_lib.untrack(IGNORED_FP_WITH_SPACE))


class TestCheckoutFile(TestFile):

  @common.assert_no_side_effects(TRACKED_FP)
  def test_checkout_fp_at_head(self):
    contents = self._read_file(TRACKED_FP)
    self._write_file(TRACKED_FP, contents='contents')
    self.assertEqual(file_lib.SUCCESS, file_lib.checkout(TRACKED_FP)[0])
    self.assertEqual(contents, self._read_file(TRACKED_FP))

  @common.assert_no_side_effects(TRACKED_FP_WITH_SPACE)
  def test_checkout_fp_with_space_at_head(self):
    contents = self._read_file(TRACKED_FP_WITH_SPACE)
    self._write_file(TRACKED_FP_WITH_SPACE, contents='contents')
    self.assertEqual(
        file_lib.SUCCESS, file_lib.checkout(TRACKED_FP_WITH_SPACE)[0])
    self.assertEqual(contents, self._read_file(TRACKED_FP_WITH_SPACE))

  def test_checkout_fp_at_cp_other_than_head(self):
    self._write_file(TRACKED_FP, contents='contents')
    self.assertEqual(
        file_lib.SUCCESS, file_lib.checkout(TRACKED_FP, 'HEAD^1')[0])
    self.assertEqual(TRACKED_FP_CONTENTS_1, self._read_file(TRACKED_FP))

  def test_checkout_fp_with_space_at_cp_other_than_head(self):
    self._write_file(TRACKED_FP_WITH_SPACE, contents='contents')
    self.assertEqual(
        file_lib.SUCCESS, file_lib.checkout(TRACKED_FP_WITH_SPACE, 'HEAD^1')[0])
    self.assertEqual(
        TRACKED_FP_CONTENTS_1, self._read_file(TRACKED_FP_WITH_SPACE))

  @common.assert_no_side_effects(UNTRACKED_FP)
  def test_checkout_uncommited_fp(self):
    self.assertEqual(
        file_lib.FILE_NOT_FOUND_AT_CP, file_lib.checkout(UNTRACKED_FP)[0])

  @common.assert_no_side_effects(UNTRACKED_FP_WITH_SPACE)
  def test_checkout_uncommited_fp(self):
    self.assertEqual(
        file_lib.FILE_NOT_FOUND_AT_CP,
        file_lib.checkout(UNTRACKED_FP_WITH_SPACE)[0])

  def test_checkout_nonexistent_fp(self):
    self.assertEqual(
        file_lib.FILE_NOT_FOUND_AT_CP, file_lib.checkout(NONEXISTENT_FP)[0])

  def test_checkout_nonexistent_fp_with_space(self):
    self.assertEqual(
        file_lib.FILE_NOT_FOUND_AT_CP,
        file_lib.checkout(NONEXISTENT_FP_WITH_SPACE)[0])


if __name__ == '__main__':
  unittest.main()
