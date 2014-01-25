# Gitless - a version control system built on top of Git.
# Copyright (c) 2013  Santiago Perez De Rosso.
# Licensed under GNU GPL, version 2.

"""Unit tests for file module."""


import os
import unittest

import gitless.core.file as file_lib
import common


TRACKED_FP = 'f1'
TRACKED_FP_CONTENTS_1 = 'f1-1\n'
TRACKED_FP_CONTENTS_2 = 'f1-2\n'
TRACKED_FP_WITH_SPACE = 'f1 space'
UNTRACKED_FP = 'f2'
UNTRACKED_FP_WITH_SPACE = 'f2 space'
IGNORED_FP = 'f3'
IGNORED_FP_WITH_SPACE = 'f3 space'
NONEXISTENT_FP = 'nonexistent'
NONEXISTENT_FP_WITH_SPACE = 'nonexistent space'
DIR = 'dir'
UNTRACKED_DIR_FP = os.path.join(DIR, 'f1')
UNTRACKED_DIR_FP_WITH_SPACE = os.path.join(DIR, 'f1 space')
TRACKED_DIR_FP = os.path.join(DIR, 'f2')
TRACKED_DIR_FP_WITH_SPACE = os.path.join(DIR, 'f2 space')
DIR_DIR = os.path.join(DIR, DIR)
UNTRACKED_DIR_DIR_FP = os.path.join(DIR_DIR, 'f1')
UNTRACKED_DIR_DIR_FP_WITH_SPACE = os.path.join(DIR_DIR, 'f1 space')
TRACKED_DIR_DIR_FP = os.path.join(DIR_DIR, 'f2')
TRACKED_DIR_DIR_FP_WITH_SPACE = os.path.join(DIR_DIR, 'f2 space')
ALL_FPS_IN_WD = [
    TRACKED_FP, TRACKED_FP_WITH_SPACE, UNTRACKED_FP, UNTRACKED_FP_WITH_SPACE,
    IGNORED_FP, IGNORED_FP_WITH_SPACE, UNTRACKED_DIR_FP,
    UNTRACKED_DIR_FP_WITH_SPACE, TRACKED_DIR_FP, TRACKED_DIR_FP_WITH_SPACE,
    UNTRACKED_DIR_DIR_FP, UNTRACKED_DIR_DIR_FP_WITH_SPACE, TRACKED_DIR_DIR_FP,
    TRACKED_DIR_DIR_FP_WITH_SPACE, '.gitignore']
ALL_DIR_FPS_IN_WD = [
    TRACKED_DIR_FP, TRACKED_DIR_FP_WITH_SPACE, UNTRACKED_DIR_FP,
    UNTRACKED_DIR_FP_WITH_SPACE, TRACKED_DIR_DIR_FP,
    TRACKED_DIR_DIR_FP_WITH_SPACE, UNTRACKED_DIR_DIR_FP,
    UNTRACKED_DIR_DIR_FP_WITH_SPACE]


class TestFile(common.TestCore):
  """Base class for file tests."""

  def setUp(self):
    super(TestFile, self).setUp()

    # Build up an interesting mock repo.
    self._write_file(TRACKED_FP, contents=TRACKED_FP_CONTENTS_1)
    self._write_file(TRACKED_FP_WITH_SPACE, contents=TRACKED_FP_CONTENTS_1)
    self._write_file(TRACKED_DIR_FP, contents=TRACKED_FP_CONTENTS_1)
    self._write_file(TRACKED_DIR_FP_WITH_SPACE, contents=TRACKED_FP_CONTENTS_1)
    self._write_file(TRACKED_DIR_DIR_FP, contents=TRACKED_FP_CONTENTS_1)
    self._write_file(
        TRACKED_DIR_DIR_FP_WITH_SPACE, contents=TRACKED_FP_CONTENTS_1)
    self._git_call(
        'add "{}" "{}" "{}" "{}" "{}" "{}"'.format(
          TRACKED_FP, TRACKED_FP_WITH_SPACE,
          TRACKED_DIR_FP, TRACKED_DIR_FP_WITH_SPACE,
          TRACKED_DIR_DIR_FP, TRACKED_DIR_DIR_FP_WITH_SPACE))
    self._git_call(
        'commit -m"1" "{}" "{}" "{}" "{}" "{}" "{}"'.format(
          TRACKED_FP, TRACKED_FP_WITH_SPACE,
          TRACKED_DIR_FP, TRACKED_DIR_FP_WITH_SPACE,
          TRACKED_DIR_DIR_FP, TRACKED_DIR_DIR_FP_WITH_SPACE))
    self._write_file(TRACKED_FP, contents=TRACKED_FP_CONTENTS_2)
    self._write_file(TRACKED_FP_WITH_SPACE, contents=TRACKED_FP_CONTENTS_2)
    self._write_file(TRACKED_DIR_FP, contents=TRACKED_FP_CONTENTS_2)
    self._write_file(TRACKED_DIR_FP_WITH_SPACE, contents=TRACKED_FP_CONTENTS_2)
    self._write_file(TRACKED_DIR_DIR_FP, contents=TRACKED_FP_CONTENTS_2)
    self._write_file(
        TRACKED_DIR_DIR_FP_WITH_SPACE, contents=TRACKED_FP_CONTENTS_2)
    self._git_call(
        'commit -m"2" "{}" "{}" "{}" "{}" "{}" "{}"'.format(
          TRACKED_FP, TRACKED_FP_WITH_SPACE,
          TRACKED_DIR_FP, TRACKED_DIR_FP_WITH_SPACE,
          TRACKED_DIR_DIR_FP, TRACKED_DIR_DIR_FP_WITH_SPACE))
    self._write_file(UNTRACKED_FP)
    self._write_file(UNTRACKED_FP_WITH_SPACE)
    self._write_file(UNTRACKED_DIR_FP)
    self._write_file(UNTRACKED_DIR_FP_WITH_SPACE)
    self._write_file(UNTRACKED_DIR_DIR_FP)
    self._write_file(UNTRACKED_DIR_DIR_FP_WITH_SPACE)
    self._write_file(
        '.gitignore', contents='{}\n{}'.format(
            IGNORED_FP, IGNORED_FP_WITH_SPACE))
    self._write_file(IGNORED_FP)
    self._write_file(IGNORED_FP_WITH_SPACE)


class TestTrackFile(TestFile):

  def test_track_dir(self):
    self.assertEqual(file_lib.FILE_IS_DIR, file_lib.track(DIR))

  @common.assert_contents_unchanged(UNTRACKED_FP)
  def test_track_untracked_fp(self):
    self.__assert_track_fp(UNTRACKED_FP)

  @common.assert_contents_unchanged(UNTRACKED_FP_WITH_SPACE)
  def test_track_untracked_fp_with_space(self):
    self.__assert_track_fp(UNTRACKED_FP_WITH_SPACE)

  @common.assert_contents_unchanged(UNTRACKED_DIR_FP)
  def test_track_untracked_dir_fp(self):
    self.__assert_track_fp(UNTRACKED_DIR_FP)

  @common.assert_contents_unchanged(UNTRACKED_DIR_FP_WITH_SPACE)
  def test_track_untracked_dir_fp_with_space(self):
    self.__assert_track_fp(UNTRACKED_DIR_FP_WITH_SPACE)

  @common.assert_contents_unchanged(UNTRACKED_DIR_DIR_FP)
  def test_track_untracked_dir_dir_fp(self):
    self.__assert_track_fp(UNTRACKED_DIR_DIR_FP)

  @common.assert_contents_unchanged(UNTRACKED_DIR_DIR_FP_WITH_SPACE)
  def test_track_untracked_dir_dir_fp_with_space(self):
    self.__assert_track_fp(UNTRACKED_DIR_DIR_FP_WITH_SPACE)

  @common.assert_contents_unchanged(
      UNTRACKED_DIR_FP, UNTRACKED_DIR_FP_WITH_SPACE, UNTRACKED_DIR_DIR_FP,
      UNTRACKED_DIR_DIR_FP_WITH_SPACE)
  def test_track_untracked_relative(self):
    os.chdir(DIR)
    self.__assert_track_fp(os.path.relpath(UNTRACKED_DIR_FP, DIR))
    self.__assert_track_fp(os.path.relpath(UNTRACKED_DIR_FP_WITH_SPACE, DIR))
    os.chdir(DIR)
    self.__assert_track_fp(os.path.relpath(UNTRACKED_DIR_DIR_FP, DIR_DIR))
    self.__assert_track_fp(
        os.path.relpath(UNTRACKED_DIR_DIR_FP_WITH_SPACE, DIR_DIR))

  def __assert_track_fp(self, fp):
    t = file_lib.track(fp)
    self.assertEqual(
        file_lib.SUCCESS, t,
        'Track of fp "{}" failed: expected {}, got {}'.format(
            fp, file_lib.SUCCESS, t))
    st = file_lib.status(fp)
    self.assertEqual(
        file_lib.TRACKED, st.type,
        'Track of fp "{}" failed: expected status.type={}, got '
        'status.type={}'.format(fp, file_lib.TRACKED, st.type))

  @common.assert_no_side_effects(TRACKED_FP)
  def test_track_tracked_fp(self):
    self.assertEqual(file_lib.FILE_ALREADY_TRACKED, file_lib.track(TRACKED_FP))

  @common.assert_no_side_effects(TRACKED_FP_WITH_SPACE)
  def test_track_tracked_fp_with_space(self):
    self.assertEqual(
        file_lib.FILE_ALREADY_TRACKED, file_lib.track(TRACKED_FP_WITH_SPACE))

  @common.assert_no_side_effects(TRACKED_DIR_FP)
  def test_track_tracked_dir_fp(self):
    self.assertEqual(
        file_lib.FILE_ALREADY_TRACKED, file_lib.track(TRACKED_DIR_FP))

  @common.assert_no_side_effects(TRACKED_DIR_FP_WITH_SPACE)
  def test_track_tracked_dir_fp_with_space(self):
    self.assertEqual(
        file_lib.FILE_ALREADY_TRACKED,
        file_lib.track(TRACKED_DIR_FP_WITH_SPACE))

  @common.assert_contents_unchanged(TRACKED_DIR_DIR_FP)
  def test_track_tracked_dir_dir_fp(self):
    self.assertEqual(
        file_lib.FILE_ALREADY_TRACKED,
        file_lib.track(TRACKED_DIR_DIR_FP))

  @common.assert_contents_unchanged(TRACKED_DIR_DIR_FP_WITH_SPACE)
  def test_track_tracked_dir_dir_fp_with_space(self):
    self.assertEqual(
        file_lib.FILE_ALREADY_TRACKED,
        file_lib.track(TRACKED_DIR_DIR_FP_WITH_SPACE))

  @common.assert_contents_unchanged(
      TRACKED_DIR_FP, TRACKED_DIR_FP_WITH_SPACE, TRACKED_DIR_DIR_FP,
      TRACKED_DIR_DIR_FP_WITH_SPACE)
  def test_track_tracked_relative(self):
    os.chdir(DIR)
    self.assertEqual(
        file_lib.FILE_ALREADY_TRACKED,
        file_lib.track(os.path.relpath(TRACKED_DIR_FP, DIR)))
    self.assertEqual(
        file_lib.FILE_ALREADY_TRACKED,
        file_lib.track(os.path.relpath(TRACKED_DIR_FP_WITH_SPACE, DIR)))
    os.chdir(DIR)
    self.assertEqual(
        file_lib.FILE_ALREADY_TRACKED,
        file_lib.track(os.path.relpath(TRACKED_DIR_DIR_FP, DIR_DIR)))
    self.assertEqual(
        file_lib.FILE_ALREADY_TRACKED,
        file_lib.track(os.path.relpath(TRACKED_DIR_DIR_FP_WITH_SPACE, DIR_DIR)))

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

  def test_untrack_dir(self):
    self.assertEqual(file_lib.FILE_IS_DIR, file_lib.untrack(DIR))

  @common.assert_contents_unchanged(TRACKED_FP)
  def test_untrack_tracked_fp(self):
    self.__assert_untrack_fp(TRACKED_FP)

  @common.assert_contents_unchanged(TRACKED_FP_WITH_SPACE)
  def test_untrack_tracked_fp_space(self):
    self.__assert_untrack_fp(TRACKED_FP_WITH_SPACE)

  @common.assert_contents_unchanged(TRACKED_DIR_FP)
  def test_untrack_tracked_dir_fp(self):
    self.__assert_untrack_fp(TRACKED_DIR_FP)

  @common.assert_contents_unchanged(TRACKED_DIR_FP_WITH_SPACE)
  def test_untrack_tracked_dir_fp_with_space(self):
    self.__assert_untrack_fp(TRACKED_DIR_FP_WITH_SPACE)

  @common.assert_contents_unchanged(TRACKED_DIR_DIR_FP)
  def test_untrack_tracked_dir_dir_fp(self):
    self.__assert_untrack_fp(TRACKED_DIR_DIR_FP)

  @common.assert_contents_unchanged(TRACKED_DIR_DIR_FP_WITH_SPACE)
  def test_untrack_tracked_dir_dir_fp_with_space(self):
    self.__assert_untrack_fp(TRACKED_DIR_DIR_FP_WITH_SPACE)

  # TODO(sperezde): change the decorator so that it accepts varargs.
  @common.assert_contents_unchanged(TRACKED_DIR_FP)
  @common.assert_contents_unchanged(TRACKED_DIR_FP_WITH_SPACE)
  @common.assert_contents_unchanged(TRACKED_DIR_DIR_FP)
  @common.assert_contents_unchanged(TRACKED_DIR_DIR_FP_WITH_SPACE)
  def test_untrack_tracked_relative(self):
    os.chdir(DIR)
    self.__assert_untrack_fp(os.path.relpath(TRACKED_DIR_FP, DIR))
    self.__assert_untrack_fp(os.path.relpath(TRACKED_DIR_FP_WITH_SPACE, DIR))
    os.chdir(DIR)
    self.__assert_untrack_fp(os.path.relpath(TRACKED_DIR_DIR_FP, DIR_DIR))
    self.__assert_untrack_fp(
        os.path.relpath(TRACKED_DIR_DIR_FP_WITH_SPACE, DIR_DIR))

  def __assert_untrack_fp(self, fp):
    t = file_lib.untrack(fp)
    self.assertEqual(
        file_lib.SUCCESS, t,
        'Untrack of fp "{}" failed: expected {}, got {}'.format(
            fp, file_lib.SUCCESS, t))
    st = file_lib.status(fp)
    self.assertEqual(
        file_lib.UNTRACKED, st.type,
        'Untrack of fp "{}" failed: expected status.type={}, got '
        'status.type={}'.format(fp, file_lib.UNTRACKED, st.type))

  @common.assert_no_side_effects(UNTRACKED_FP)
  def test_untrack_untracked_fp(self):
    self.assertEqual(
        file_lib.FILE_ALREADY_UNTRACKED, file_lib.untrack(UNTRACKED_FP))

  @common.assert_no_side_effects(UNTRACKED_FP_WITH_SPACE)
  def test_untrack_untracked_fp_with_space(self):
    self.assertEqual(
        file_lib.FILE_ALREADY_UNTRACKED,
        file_lib.untrack(UNTRACKED_FP_WITH_SPACE))

  @common.assert_no_side_effects(UNTRACKED_DIR_FP)
  def test_untrack_untracked_dir_fp(self):
    self.assertEqual(
        file_lib.FILE_ALREADY_UNTRACKED, file_lib.untrack(UNTRACKED_DIR_FP))

  @common.assert_no_side_effects(UNTRACKED_DIR_FP_WITH_SPACE)
  def test_untrack_untracked_dir_fp_with_space(self):
    self.assertEqual(
        file_lib.FILE_ALREADY_UNTRACKED,
        file_lib.untrack(UNTRACKED_DIR_FP_WITH_SPACE))

  @common.assert_no_side_effects(UNTRACKED_DIR_DIR_FP)
  def test_untrack_untracked_dir_dir_fp(self):
    self.assertEqual(
        file_lib.FILE_ALREADY_UNTRACKED, file_lib.untrack(UNTRACKED_DIR_DIR_FP))

  @common.assert_no_side_effects(UNTRACKED_DIR_DIR_FP_WITH_SPACE)
  def test_untrack_untracked_dir_dir_fp_with_space(self):
    self.assertEqual(
        file_lib.FILE_ALREADY_UNTRACKED,
        file_lib.untrack(UNTRACKED_DIR_DIR_FP_WITH_SPACE))

  # TODO(sperezde): change the decorator so that it accepts varargs.
  @common.assert_contents_unchanged(UNTRACKED_DIR_FP)
  @common.assert_contents_unchanged(UNTRACKED_DIR_FP_WITH_SPACE)
  @common.assert_contents_unchanged(UNTRACKED_DIR_DIR_FP)
  @common.assert_contents_unchanged(UNTRACKED_DIR_DIR_FP_WITH_SPACE)
  def test_untrack_untracked_relative(self):
    os.chdir(DIR)
    self.assertEqual(
        file_lib.FILE_ALREADY_UNTRACKED,
        file_lib.untrack(os.path.relpath(UNTRACKED_DIR_FP, DIR)))
    self.assertEqual(
        file_lib.FILE_ALREADY_UNTRACKED,
        file_lib.untrack(os.path.relpath(UNTRACKED_DIR_FP_WITH_SPACE, DIR)))
    os.chdir(DIR)
    self.assertEqual(
        file_lib.FILE_ALREADY_UNTRACKED,
        file_lib.untrack(os.path.relpath(UNTRACKED_DIR_DIR_FP, DIR_DIR)))
    self.assertEqual(
        file_lib.FILE_ALREADY_UNTRACKED,
        file_lib.untrack(
            os.path.relpath(UNTRACKED_DIR_DIR_FP_WITH_SPACE, DIR_DIR)))

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

  def test_checkout_dir(self):
    self.assertEqual(file_lib.FILE_IS_DIR, file_lib.checkout(DIR)[0])

  @common.assert_no_side_effects(TRACKED_FP)
  def test_checkout_fp_at_head(self):
    self.__assert_checkout_fp_at_head(TRACKED_FP)

  @common.assert_no_side_effects(TRACKED_FP_WITH_SPACE)
  def test_checkout_fp_with_space_at_head(self):
    self.__assert_checkout_fp_at_head(TRACKED_FP_WITH_SPACE)

  @common.assert_no_side_effects(TRACKED_DIR_FP)
  def test_checkout_dir_fp_at_head(self):
    self.__assert_checkout_fp_at_head(TRACKED_DIR_FP)

  @common.assert_no_side_effects(TRACKED_DIR_FP_WITH_SPACE)
  def test_checkout_dir_fp_with_space_at_head(self):
    self.__assert_checkout_fp_at_head(TRACKED_DIR_FP_WITH_SPACE)

  @common.assert_no_side_effects(TRACKED_DIR_DIR_FP)
  def test_checkout_dir_dir_fp_at_head(self):
    self.__assert_checkout_fp_at_head(TRACKED_DIR_DIR_FP)

  @common.assert_no_side_effects(TRACKED_DIR_DIR_FP_WITH_SPACE)
  def test_checkout_dir_dir_fp_with_space_at_head(self):
    self.__assert_checkout_fp_at_head(TRACKED_DIR_DIR_FP_WITH_SPACE)

  def test_checkout_fp_at_cp_other_than_head(self):
    self.__assert_checkout_cp_other_than_head(TRACKED_FP)

  def test_checkout_fp_with_space_at_cp_other_than_head(self):
    self.__assert_checkout_cp_other_than_head(TRACKED_FP_WITH_SPACE)

  def test_checkout_dir_fp_at_cp_other_than_head(self):
    self.__assert_checkout_cp_other_than_head(TRACKED_DIR_FP)

  def test_checkout_dir_fp_with_space_at_cp_other_than_head(self):
    self.__assert_checkout_cp_other_than_head(TRACKED_DIR_FP_WITH_SPACE)

  def test_checkout_dir_dir_fp_at_cp_other_than_head(self):
    self.__assert_checkout_cp_other_than_head(TRACKED_DIR_DIR_FP)

  def test_checkout_dir_dir_fp_with_space_at_cp_other_than_head(self):
    self.__assert_checkout_cp_other_than_head(TRACKED_DIR_DIR_FP_WITH_SPACE)

  @common.assert_no_side_effects(UNTRACKED_FP)
  def test_checkout_uncommited_fp(self):
    self.assertEqual(
        file_lib.FILE_NOT_FOUND_AT_CP, file_lib.checkout(UNTRACKED_FP)[0])

  @common.assert_no_side_effects(UNTRACKED_FP_WITH_SPACE)
  def test_checkout_uncommited_fp_with_space(self):
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

  def test_checkout_relative(self):
    os.chdir(DIR)
    self.__assert_checkout_fp_at_head(os.path.relpath(TRACKED_DIR_FP, DIR))
    self.__assert_checkout_fp_at_head(
        os.path.relpath(TRACKED_DIR_FP_WITH_SPACE, DIR))
    os.chdir(DIR)
    self.__assert_checkout_fp_at_head(
        os.path.relpath(TRACKED_DIR_DIR_FP, DIR_DIR))
    self.__assert_checkout_fp_at_head(
        os.path.relpath(TRACKED_DIR_DIR_FP_WITH_SPACE, DIR_DIR))

  def __assert_checkout_fp_at_head(self, fp):
    contents = self._read_file(fp)
    self._write_file(fp, contents='contents')
    self.assertEqual(file_lib.SUCCESS, file_lib.checkout(fp)[0])
    self.assertEqual(contents, self._read_file(fp))

  def __assert_checkout_cp_other_than_head(self, fp):
    self._write_file(fp, contents='contents')
    self.assertEqual(file_lib.SUCCESS, file_lib.checkout(fp, 'HEAD^1')[0])
    self.assertEqual(TRACKED_FP_CONTENTS_1, self._read_file(fp))


class TestStatus(TestFile):

  def test_status_all(self):
    st_all = file_lib.status_all()
    seen = []
    for fp, type, exists_in_lr, exists_in_wd, modified, _, _ in st_all:
      if (fp == TRACKED_FP or fp == TRACKED_FP_WITH_SPACE or
          fp == TRACKED_DIR_FP or fp == TRACKED_DIR_FP_WITH_SPACE or
          fp == TRACKED_DIR_DIR_FP or fp == TRACKED_DIR_DIR_FP_WITH_SPACE):
        self.__assert_type(fp, file_lib.TRACKED, type)
        self.__assert_field(fp, 'exists_in_lr', True, exists_in_lr)
        self.__assert_field(fp, 'modified', False, modified)
      elif (fp == UNTRACKED_FP or fp == UNTRACKED_FP_WITH_SPACE or
            fp == UNTRACKED_DIR_FP or fp == UNTRACKED_DIR_FP_WITH_SPACE or
            fp == UNTRACKED_DIR_DIR_FP or
            fp == UNTRACKED_DIR_DIR_FP_WITH_SPACE):
        self.__assert_type(fp, file_lib.UNTRACKED, type)
        self.__assert_field(fp, 'exists_in_lr', False, exists_in_lr)
        self.__assert_field(fp, 'modified', True, modified)
      elif fp == IGNORED_FP or fp == IGNORED_FP_WITH_SPACE:
        self.__assert_type(fp, file_lib.IGNORED, type)
        self.__assert_field(fp, 'exists_in_lr', False, exists_in_lr)
        self.__assert_field(fp, 'modified', True, modified)
      elif fp == '.gitignore':
        self.__assert_type(fp, file_lib.UNTRACKED, type)
        self.__assert_field(fp, 'exists_in_lr', False, exists_in_lr)
        self.__assert_field(fp, 'modified', True, modified)
      else:
        self.fail('Unexpected fp {}'.format(fp))
      self.__assert_field(fp, 'exists_in_wd', True, exists_in_wd)
      seen.append(fp)
    self.assertItemsEqual(seen, ALL_FPS_IN_WD)

  def test_status_equivalence(self):
    self.assertItemsEqual(
        file_lib.status_all(), [file_lib.status(fp) for fp in ALL_FPS_IN_WD])

  def test_status_nonexistent_fp(self):
    self.assertEqual(file_lib.FILE_NOT_FOUND, file_lib.status(NONEXISTENT_FP))

  def test_status_nonexistent_fp_with_space(self):
    self.assertEqual(
        file_lib.FILE_NOT_FOUND, file_lib.status(NONEXISTENT_FP_WITH_SPACE))

  def test_status_modify(self):
    self._write_file(TRACKED_FP, contents='contents')
    self.assertTrue(file_lib.status(TRACKED_FP).modified)
    self._write_file(TRACKED_FP, contents=TRACKED_FP_CONTENTS_2)
    self.assertFalse(file_lib.status(TRACKED_FP).modified)

  def test_status_rm(self):
    os.remove(TRACKED_FP)
    st = file_lib.status(TRACKED_FP)
    self.assertEqual(file_lib.TRACKED, st.type)
    self.assertTrue(st.modified)
    self.assertTrue(st.exists_in_lr)
    self.assertFalse(st.exists_in_wd)

    self._write_file(TRACKED_FP, contents=TRACKED_FP_CONTENTS_2)
    st = file_lib.status(TRACKED_FP)
    self.assertEqual(file_lib.TRACKED, st.type)
    self.assertFalse(st.modified)
    self.assertTrue(st.exists_in_lr)
    self.assertTrue(st.exists_in_wd)

  def test_status_track_rm(self):
    file_lib.track(UNTRACKED_FP)
    st = file_lib.status(UNTRACKED_FP)
    self.assertEqual(file_lib.TRACKED, st.type)
    self.assertTrue(st.modified)

    os.remove(UNTRACKED_FP)
    self.assertEqual(file_lib.FILE_NOT_FOUND, file_lib.status(UNTRACKED_FP))

  def test_status_track_untrack(self):
    file_lib.track(UNTRACKED_FP)
    st = file_lib.status(UNTRACKED_FP)
    self.assertEqual(file_lib.TRACKED, st.type)
    self.assertTrue(st.modified)

    file_lib.untrack(UNTRACKED_FP)
    st = file_lib.status(UNTRACKED_FP)
    self.assertEqual(file_lib.UNTRACKED, st.type)
    self.assertTrue(st.modified)

  def test_status_unignore(self):
    self._write_file('.gitignore', contents='')
    self.assertEqual(file_lib.UNTRACKED, file_lib.status(IGNORED_FP).type)
    self.assertEqual(
        file_lib.UNTRACKED, file_lib.status(IGNORED_FP_WITH_SPACE).type)

  def test_status_ignore(self):
    contents = self._read_file('.gitignore') + '\n' + TRACKED_FP
    self._write_file('.gitignore', contents=contents)
    # Tracked files can't be ignored.
    self.assertEqual(file_lib.TRACKED, file_lib.status(TRACKED_FP).type)

  def test_status_untrack_tracked_modify(self):
    file_lib.untrack(TRACKED_FP)
    st = file_lib.status(TRACKED_FP)
    self.assertEqual(file_lib.UNTRACKED, st.type)
    # self.assertFalse(st.modified)

    self._write_file(TRACKED_FP, contents='contents')
    st = file_lib.status(TRACKED_FP)
    self.assertEqual(file_lib.UNTRACKED, st.type)
    self.assertTrue(st.modified)

  def test_status_untrack_tracked_rm(self):
    file_lib.untrack(TRACKED_FP)
    st = file_lib.status(TRACKED_FP)
    self.assertEqual(file_lib.UNTRACKED, st.type)

    os.remove(TRACKED_FP)
    self.assertEqual(file_lib.FILE_NOT_FOUND, file_lib.status(TRACKED_FP))

  def test_status_all_relative(self):
    rel_to_dir = lambda fp: os.path.relpath(fp, DIR)

    os.chdir(DIR)

    st_all = file_lib.status_all()
    seen = []
    for fp, type, exists_in_lr, exists_in_wd, modified, _, _ in st_all:
      if (fp == rel_to_dir(TRACKED_DIR_FP) or
          fp == rel_to_dir(TRACKED_DIR_FP_WITH_SPACE) or
          fp == rel_to_dir(TRACKED_DIR_DIR_FP) or
          fp == rel_to_dir(TRACKED_DIR_DIR_FP_WITH_SPACE)):
        self.__assert_type(fp, file_lib.TRACKED, type)
        self.__assert_field(fp, 'exists_in_lr', True, exists_in_lr)
        self.__assert_field(fp, 'modified', False, modified)
      elif (fp == rel_to_dir(UNTRACKED_DIR_FP) or
            fp == rel_to_dir(UNTRACKED_DIR_FP_WITH_SPACE) or
            fp == rel_to_dir(UNTRACKED_DIR_DIR_FP) or
            fp == rel_to_dir(UNTRACKED_DIR_DIR_FP_WITH_SPACE)):
        self.__assert_type(fp, file_lib.UNTRACKED, type)
        self.__assert_field(fp, 'exists_in_lr', False, exists_in_lr)
        self.__assert_field(fp, 'modified', True, modified)
      else:
        self.fail('Unexpected fp {}'.format(fp))
      self.__assert_field(fp, 'exists_in_wd', True, exists_in_wd)
      seen.append(fp)
    self.assertItemsEqual(seen, [rel_to_dir(fp) for fp in ALL_DIR_FPS_IN_WD])

  def test_status_ignore_tracked(self):
    """Assert that ignoring a tracked file has no effect."""
    self._append_to_file('.gitignore', contents='\n' + TRACKED_FP + '\n')
    self.__assert_type(
        TRACKED_FP, file_lib.TRACKED, file_lib.status(TRACKED_FP).type)

  def test_status_ignore_untracked(self):
    """Assert that ignoring a untracked file makes it ignored."""
    self._append_to_file('.gitignore', contents='\n' + UNTRACKED_FP + '\n')
    self.__assert_type(
        UNTRACKED_FP, file_lib.IGNORED, file_lib.status(UNTRACKED_FP).type)

  # TODO(sperezde): this test exposes a rough edge that we haven't fixed yet.
  # Uncomment the test once it's fixed.
  #def test_status_ignore_untracked_tracked(self):
  #  file_lib.untrack(TRACKED_FP)
  #  self._append_to_file('.gitignore', contents='\n' + TRACKED_FP + '\n')
  #  self.__assert_type(
  #      TRACKED_FP, file_lib.IGNORED, file_lib.status(TRACKED_FP).type)

  def __assert_type(self, fp, expected, got):
    self.assertEqual(
        expected, got,
        'Incorrect type for {}: expected {}, got {}'.format(
            fp, expected, got))

  def __assert_field(self, fp, field, expected, got):
     self.assertEqual(
         expected, got,
         'Incorrect status for {}: expected {}={}, got {}={}'.format(
             fp, field, expected, field, got))


class TestDiff(TestFile):

  # TODO(sperezde): add DIR, DIR_DIR, relative tests to diff.

  def test_diff_dir(self):
    self.assertEqual(file_lib.FILE_IS_DIR, file_lib.diff(DIR)[0])

  @common.assert_no_side_effects(UNTRACKED_FP)
  def test_diff_untracked_fp(self):
    self.assertEqual(file_lib.FILE_IS_UNTRACKED, file_lib.diff(UNTRACKED_FP)[0])

  @common.assert_no_side_effects(UNTRACKED_FP_WITH_SPACE)
  def test_diff_untracked_fp_with_space(self):
    self.assertEqual(
        file_lib.FILE_IS_UNTRACKED, file_lib.diff(UNTRACKED_FP_WITH_SPACE)[0])

  @common.assert_no_side_effects(IGNORED_FP)
  def test_diff_ignored_fp(self):
    self.assertEqual(file_lib.FILE_IS_IGNORED, file_lib.diff(IGNORED_FP)[0])

  @common.assert_no_side_effects(IGNORED_FP_WITH_SPACE)
  def test_diff_ignored_fp_with_space(self):
    self.assertEqual(
        file_lib.FILE_IS_IGNORED, file_lib.diff(IGNORED_FP_WITH_SPACE)[0])

  def test_diff_nonexistent_fp(self):
    self.assertEqual(file_lib.FILE_NOT_FOUND, file_lib.diff(NONEXISTENT_FP)[0])

  def test_diff_nonexistent_fp_with_space(self):
    self.assertEqual(
        file_lib.FILE_NOT_FOUND, file_lib.diff(NONEXISTENT_FP_WITH_SPACE)[0])

  @common.assert_no_side_effects(TRACKED_FP)
  def test_empty_diff(self):
    ret, (out, _) = file_lib.diff(TRACKED_FP)
    self.assertEqual(file_lib.SUCCESS, ret)
    self.assertEqual([], out)

  def test_diff_basic(self):
    self._write_file(TRACKED_FP, contents='new contents')
    ret, (out, _) = file_lib.diff(TRACKED_FP)

    self.assertEqual(file_lib.SUCCESS, ret)
    self.assertEqual(3, len(out))
    # [:-1] removes the '\n'.
    self.assertEqual('-' + TRACKED_FP_CONTENTS_2[:-1], out[1].line)
    self.assertEqual(file_lib.DIFF_MINUS, out[1].status)
    self.assertEqual(1, out[1].old_line_number)
    self.assertEqual(None, out[1].new_line_number)

    self.assertEqual('+new contents', out[2].line)
    self.assertEqual(file_lib.DIFF_ADDED, out[2].status)
    self.assertEqual(None, out[2].old_line_number)
    self.assertEqual(1, out[2].new_line_number)

  def test_diff_append(self):
    self._append_to_file(TRACKED_FP, contents='new contents')
    ret, (out, _) = file_lib.diff(TRACKED_FP)

    self.assertEqual(file_lib.SUCCESS, ret)
    self.assertEqual(3, len(out))
    # [:-1] removes the '\n'.
    self.assertEqual(' ' + TRACKED_FP_CONTENTS_2[:-1], out[1].line)
    self.assertEqual(file_lib.DIFF_SAME, out[1].status)
    self.assertEqual(1, out[1].old_line_number)
    self.assertEqual(1, out[1].new_line_number)

    self.assertEqual('+new contents', out[2].line)
    self.assertEqual(file_lib.DIFF_ADDED, out[2].status)
    self.assertEqual(None, out[2].old_line_number)
    self.assertEqual(2, out[2].new_line_number)

  def test_diff_new_fp(self):
    fp = 'new'
    self._write_file(fp, contents=fp + '\n')
    file_lib.track(fp)
    ret, (out, _) = file_lib.diff(fp)

    self.assertEqual(file_lib.SUCCESS, ret)
    self.assertEqual(2, len(out))
    self.assertEqual('+' + fp, out[1].line)
    self.assertEqual(file_lib.DIFF_ADDED, out[1].status)
    self.assertEqual(None, out[1].old_line_number)
    self.assertEqual(1, out[1].new_line_number)

    # Now let's add some change to the file and check that diff notices it.
    self._append_to_file(fp, contents='new line')
    ret, (out, _) = file_lib.diff(fp)

    self.assertEqual(file_lib.SUCCESS, ret)

    self.assertEqual(3, len(out))
    self.assertEqual('+' + fp, out[1].line)
    self.assertEqual(file_lib.DIFF_ADDED, out[1].status)
    self.assertEqual(None, out[1].old_line_number)
    self.assertEqual(1, out[1].new_line_number)

    self.assertEqual('+new line', out[2].line)
    self.assertEqual(file_lib.DIFF_ADDED, out[2].status)
    self.assertEqual(None, out[2].old_line_number)
    self.assertEqual(2, out[2].new_line_number)


FP_IN_CONFLICT = 'f_conflict'
DIR_FP_IN_CONFLICT = os.path.join(DIR, FP_IN_CONFLICT)


class TestResolveFile(TestFile):

  def setUp(self):
    super(TestResolveFile, self).setUp()

    # Generate a conflict.
    self._git_call('checkout -b branch')
    self._write_file(FP_IN_CONFLICT, contents='branch')
    self._write_file(DIR_FP_IN_CONFLICT, contents='branch')
    self._git_call('add "{}" "{}"'.format(FP_IN_CONFLICT, DIR_FP_IN_CONFLICT))
    self._git_call(
        'commit -m"branch" "{}" "{}"'.format(
            FP_IN_CONFLICT, DIR_FP_IN_CONFLICT))
    self._git_call('checkout master')
    self._write_file(FP_IN_CONFLICT, contents='master')
    self._write_file(DIR_FP_IN_CONFLICT, contents='master')
    self._git_call('add "{}" "{}"'.format(FP_IN_CONFLICT, DIR_FP_IN_CONFLICT))
    self._git_call(
        'commit -m"master" "{}" "{}"'.format(
            FP_IN_CONFLICT, DIR_FP_IN_CONFLICT))
    self._git_call('merge branch', expected_ret_code=1)

  def test_resolve_dir(self):
    self.assertEqual(file_lib.FILE_IS_DIR, file_lib.resolve(DIR))

  @common.assert_no_side_effects(TRACKED_FP)
  def test_resolve_fp_with_no_conflicts(self):
    self.assertEqual(
        file_lib.FILE_NOT_IN_CONFLICT, file_lib.resolve(TRACKED_FP))

  def test_resolve_fp_with_conflicts(self):
    self.__assert_resolve_fp(FP_IN_CONFLICT)

  def test_resolve_dir_fp_with_conflicts(self):
    self.__assert_resolve_fp(DIR_FP_IN_CONFLICT)

  def test_resolve_relative(self):
    self.__assert_resolve_fp(DIR_FP_IN_CONFLICT)
    os.chdir(DIR)
    rel_fp = os.path.relpath(DIR_FP_IN_CONFLICT, DIR)
    self.assertTrue(file_lib.status(rel_fp).resolved)
    self.assertEqual(file_lib.FILE_ALREADY_RESOLVED, file_lib.resolve(rel_fp))

  @common.assert_contents_unchanged(FP_IN_CONFLICT)
  def __assert_resolve_fp(self, fp):
    self.assertEqual(file_lib.SUCCESS, file_lib.resolve(fp))
    self.assertTrue(file_lib.status(fp).resolved)


if __name__ == '__main__':
  unittest.main()
