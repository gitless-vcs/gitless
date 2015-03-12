# Gitless - a version control system built on top of Git.
# Licensed under GNU GPL v2.

"""Unit tests for file module."""


import os

from gitless import core
import gitless.tests.utils as utils_lib

from . import common


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
    utils_lib.write_file(TRACKED_FP, contents=TRACKED_FP_CONTENTS_1)
    utils_lib.write_file(TRACKED_FP_WITH_SPACE, contents=TRACKED_FP_CONTENTS_1)
    utils_lib.write_file(TRACKED_DIR_FP, contents=TRACKED_FP_CONTENTS_1)
    utils_lib.write_file(
        TRACKED_DIR_FP_WITH_SPACE, contents=TRACKED_FP_CONTENTS_1)
    utils_lib.write_file(TRACKED_DIR_DIR_FP, contents=TRACKED_FP_CONTENTS_1)
    utils_lib.write_file(
        TRACKED_DIR_DIR_FP_WITH_SPACE, contents=TRACKED_FP_CONTENTS_1)
    utils_lib.git_call(
        'add "{0}" "{1}" "{2}" "{3}" "{4}" "{5}"'.format(
          TRACKED_FP, TRACKED_FP_WITH_SPACE,
          TRACKED_DIR_FP, TRACKED_DIR_FP_WITH_SPACE,
          TRACKED_DIR_DIR_FP, TRACKED_DIR_DIR_FP_WITH_SPACE))
    utils_lib.git_call(
        'commit -m"1" "{0}" "{1}" "{2}" "{3}" "{4}" "{5}"'.format(
          TRACKED_FP, TRACKED_FP_WITH_SPACE,
          TRACKED_DIR_FP, TRACKED_DIR_FP_WITH_SPACE,
          TRACKED_DIR_DIR_FP, TRACKED_DIR_DIR_FP_WITH_SPACE))
    utils_lib.write_file(TRACKED_FP, contents=TRACKED_FP_CONTENTS_2)
    utils_lib.write_file(TRACKED_FP_WITH_SPACE, contents=TRACKED_FP_CONTENTS_2)
    utils_lib.write_file(TRACKED_DIR_FP, contents=TRACKED_FP_CONTENTS_2)
    utils_lib.write_file(
        TRACKED_DIR_FP_WITH_SPACE, contents=TRACKED_FP_CONTENTS_2)
    utils_lib.write_file(TRACKED_DIR_DIR_FP, contents=TRACKED_FP_CONTENTS_2)
    utils_lib.write_file(
        TRACKED_DIR_DIR_FP_WITH_SPACE, contents=TRACKED_FP_CONTENTS_2)
    utils_lib.git_call(
        'commit -m"2" "{0}" "{1}" "{2}" "{3}" "{4}" "{5}"'.format(
          TRACKED_FP, TRACKED_FP_WITH_SPACE,
          TRACKED_DIR_FP, TRACKED_DIR_FP_WITH_SPACE,
          TRACKED_DIR_DIR_FP, TRACKED_DIR_DIR_FP_WITH_SPACE))
    utils_lib.write_file(UNTRACKED_FP)
    utils_lib.write_file(UNTRACKED_FP_WITH_SPACE)
    utils_lib.write_file(UNTRACKED_DIR_FP)
    utils_lib.write_file(UNTRACKED_DIR_FP_WITH_SPACE)
    utils_lib.write_file(UNTRACKED_DIR_DIR_FP)
    utils_lib.write_file(UNTRACKED_DIR_DIR_FP_WITH_SPACE)
    utils_lib.write_file(
        '.gitignore', contents='{0}\n{1}'.format(
            IGNORED_FP, IGNORED_FP_WITH_SPACE))
    utils_lib.write_file(IGNORED_FP)
    utils_lib.write_file(IGNORED_FP_WITH_SPACE)

    self.curr_b = self.repo.current_branch


class TestTrackFile(TestFile):

  def __assert_track_untracked(self, *fps):
    root = self.repo.root
    for fp in fps:
      fp = os.path.relpath(fp, root)
      self.curr_b.track_file(fp)
      st = self.curr_b.status_file(fp)
      self.assertEqual(
          core.GL_STATUS_TRACKED, st.type,
          'Track of fp "{0}" failed: expected status.type={1}, got '
          'status.type={2}'.format(fp, core.GL_STATUS_TRACKED, st.type))

  @common.assert_contents_unchanged(
      UNTRACKED_FP, UNTRACKED_FP_WITH_SPACE,
      UNTRACKED_DIR_FP, UNTRACKED_DIR_FP_WITH_SPACE,
      UNTRACKED_DIR_DIR_FP, UNTRACKED_DIR_DIR_FP_WITH_SPACE)
  def test_track_untracked(self):
    self.__assert_track_untracked(
        UNTRACKED_FP, UNTRACKED_FP_WITH_SPACE,
        UNTRACKED_DIR_FP, UNTRACKED_DIR_FP_WITH_SPACE,
        UNTRACKED_DIR_DIR_FP, UNTRACKED_DIR_DIR_FP_WITH_SPACE)

  @common.assert_contents_unchanged(
      UNTRACKED_DIR_FP, UNTRACKED_DIR_FP_WITH_SPACE,
      UNTRACKED_DIR_DIR_FP, UNTRACKED_DIR_DIR_FP_WITH_SPACE)
  def test_track_untracked_relative(self):
    os.chdir(DIR)
    self.__assert_track_untracked(
        os.path.relpath(UNTRACKED_DIR_FP, DIR),
        os.path.relpath(UNTRACKED_DIR_FP_WITH_SPACE, DIR))
    os.chdir(DIR)
    self.__assert_track_untracked(
        os.path.relpath(UNTRACKED_DIR_DIR_FP, DIR_DIR),
        os.path.relpath(UNTRACKED_DIR_DIR_FP_WITH_SPACE, DIR_DIR))

  def __assert_track_tracked(self, *fps):
    root = self.repo.root
    for fp in fps:
      fp = os.path.relpath(fp, root)
      self.assertRaisesRegexp(
          ValueError, 'already tracked', self.curr_b.track_file, fp)

  @common.assert_no_side_effects(
      TRACKED_FP, TRACKED_FP_WITH_SPACE,
      TRACKED_DIR_FP, TRACKED_DIR_FP_WITH_SPACE,
      TRACKED_DIR_DIR_FP, TRACKED_DIR_DIR_FP_WITH_SPACE)
  def test_track_tracked_fp(self):
    self.__assert_track_tracked(
        TRACKED_FP, TRACKED_FP_WITH_SPACE,
        TRACKED_DIR_FP, TRACKED_DIR_FP_WITH_SPACE,
        TRACKED_DIR_DIR_FP, TRACKED_DIR_DIR_FP_WITH_SPACE)

  @common.assert_no_side_effects(
      TRACKED_DIR_FP, TRACKED_DIR_FP_WITH_SPACE,
      TRACKED_DIR_DIR_FP, TRACKED_DIR_DIR_FP_WITH_SPACE)
  def test_track_tracked_relative(self):
    os.chdir(DIR)
    self.__assert_track_tracked(
        os.path.relpath(TRACKED_DIR_FP, DIR),
        os.path.relpath(TRACKED_DIR_FP_WITH_SPACE, DIR))
    os.chdir(DIR)
    self.__assert_track_tracked(
        os.path.relpath(TRACKED_DIR_DIR_FP, DIR_DIR),
        os.path.relpath(TRACKED_DIR_DIR_FP_WITH_SPACE, DIR_DIR))

  def __assert_track_nonexistent_fp(self, *fps):
    root = self.repo.root
    for fp in fps:
      fp = os.path.relpath(fp, root)
      self.assertRaises(KeyError, self.curr_b.track_file, fp)

  def test_track_nonexistent_fp(self):
    self.__assert_track_nonexistent_fp(
        NONEXISTENT_FP, NONEXISTENT_FP_WITH_SPACE)

  def __assert_track_ignored(self, *fps):
    root = self.repo.root
    for fp in fps:
      fp = os.path.relpath(fp, root)
      self.assertRaisesRegexp(
          ValueError, 'is ignored', self.curr_b.track_file, fp)

  @common.assert_no_side_effects(IGNORED_FP, IGNORED_FP_WITH_SPACE)
  def test_track_ignored(self):
    self.__assert_track_ignored(IGNORED_FP, IGNORED_FP_WITH_SPACE)


class TestUntrackFile(TestFile):

  def __assert_untrack_tracked(self, *fps):
    root = self.repo.root
    for fp in fps:
      fp = os.path.relpath(fp, root)
      self.curr_b.untrack_file(fp)
      st = self.curr_b.status_file(fp)
      self.assertEqual(
          core.GL_STATUS_UNTRACKED, st.type,
          'Untrack of fp "{0}" failed: expected status.type={1}, got '
          'status.type={2}'.format(fp, core.GL_STATUS_UNTRACKED, st.type))

  @common.assert_contents_unchanged(
      TRACKED_FP, TRACKED_FP_WITH_SPACE,
      TRACKED_DIR_FP, TRACKED_DIR_FP_WITH_SPACE,
      TRACKED_DIR_DIR_FP, TRACKED_DIR_DIR_FP_WITH_SPACE)
  def test_untrack_tracked(self):
    self.__assert_untrack_tracked(
        TRACKED_FP, TRACKED_FP_WITH_SPACE,
        TRACKED_DIR_FP, TRACKED_DIR_FP_WITH_SPACE,
        TRACKED_DIR_DIR_FP, TRACKED_DIR_DIR_FP_WITH_SPACE)

  @common.assert_contents_unchanged(
      TRACKED_DIR_FP, TRACKED_DIR_FP_WITH_SPACE,
      TRACKED_DIR_DIR_FP, TRACKED_DIR_DIR_FP_WITH_SPACE)
  def test_untrack_tracked_relative(self):
    os.chdir(DIR)
    self.__assert_untrack_tracked(
        os.path.relpath(TRACKED_DIR_FP, DIR),
        os.path.relpath(TRACKED_DIR_FP_WITH_SPACE, DIR))
    os.chdir(DIR)
    self.__assert_untrack_tracked(
        os.path.relpath(TRACKED_DIR_DIR_FP, DIR_DIR),
        os.path.relpath(TRACKED_DIR_DIR_FP_WITH_SPACE, DIR_DIR))

  def __assert_untrack_error(self, msg, *fps):
    root = self.repo.root
    for fp in fps:
      fp = os.path.relpath(fp, root)
      self.assertRaisesRegexp(ValueError, msg, self.curr_b.untrack_file, fp)

  def __assert_untrack_untracked(self, *fps):
    self.__assert_untrack_error('already untracked', *fps)

  @common.assert_no_side_effects(
      UNTRACKED_FP, UNTRACKED_FP_WITH_SPACE,
      UNTRACKED_DIR_FP, UNTRACKED_DIR_FP_WITH_SPACE,
      UNTRACKED_DIR_DIR_FP, UNTRACKED_DIR_DIR_FP_WITH_SPACE)
  def test_untrack_untracked_fp(self):
    self.__assert_untrack_untracked(
        UNTRACKED_FP, UNTRACKED_FP_WITH_SPACE,
        UNTRACKED_DIR_FP, UNTRACKED_DIR_FP_WITH_SPACE,
        UNTRACKED_DIR_DIR_FP, UNTRACKED_DIR_DIR_FP_WITH_SPACE)

  @common.assert_contents_unchanged(
      UNTRACKED_DIR_FP, UNTRACKED_DIR_FP_WITH_SPACE,
      UNTRACKED_DIR_DIR_FP, UNTRACKED_DIR_DIR_FP_WITH_SPACE)
  def test_untrack_untracked_relative(self):
    os.chdir(DIR)
    self.__assert_untrack_untracked(
        os.path.relpath(UNTRACKED_DIR_FP, DIR),
        os.path.relpath(UNTRACKED_DIR_FP_WITH_SPACE, DIR))
    os.chdir(DIR)
    self.__assert_untrack_untracked(
        os.path.relpath(UNTRACKED_DIR_DIR_FP, DIR_DIR),
        os.path.relpath(UNTRACKED_DIR_DIR_FP_WITH_SPACE, DIR_DIR))


  def __assert_untrack_nonexistent_fp(self, *fps):
    root = self.repo.root
    for fp in fps:
      fp = os.path.relpath(fp, root)
      self.assertRaises(KeyError, self.curr_b.untrack_file, fp)

  def test_untrack_nonexistent_fp(self):
    self.__assert_untrack_nonexistent_fp(
        NONEXISTENT_FP, NONEXISTENT_FP_WITH_SPACE)


  def __assert_untrack_ignored(self, *fps):
    self.__assert_untrack_error('is ignored', *fps)

  @common.assert_no_side_effects(IGNORED_FP, IGNORED_FP_WITH_SPACE)
  def test_untrack_ignored(self):
    self.__assert_untrack_ignored(IGNORED_FP, IGNORED_FP_WITH_SPACE)


class TestCheckoutFile(TestFile):

  def __assert_checkout_head(self, *fps):
    root = self.repo.root
    for fp in fps:
      utils_lib.write_file(fp, contents='contents')
      self.curr_b.checkout_file(
          os.path.relpath(fp, root), self.repo.revparse_single('HEAD'))
      self.assertEqual(TRACKED_FP_CONTENTS_2, utils_lib.read_file(fp))

  @common.assert_no_side_effects(
      TRACKED_FP, TRACKED_FP_WITH_SPACE,
      TRACKED_DIR_FP, TRACKED_DIR_FP_WITH_SPACE,
      TRACKED_DIR_DIR_FP, TRACKED_DIR_DIR_FP_WITH_SPACE)
  def test_checkout_head(self):
    self.__assert_checkout_head(
        TRACKED_FP, TRACKED_FP_WITH_SPACE,
        TRACKED_DIR_FP, TRACKED_DIR_FP_WITH_SPACE,
        TRACKED_DIR_DIR_FP, TRACKED_DIR_DIR_FP_WITH_SPACE)

  @common.assert_no_side_effects(
      TRACKED_FP, TRACKED_FP_WITH_SPACE,
      TRACKED_DIR_FP, TRACKED_DIR_FP_WITH_SPACE,
      TRACKED_DIR_DIR_FP, TRACKED_DIR_DIR_FP_WITH_SPACE)
  def test_checkout_head_relative(self):
    os.chdir(DIR)
    self.__assert_checkout_head(os.path.relpath(TRACKED_DIR_FP, DIR))
    self.__assert_checkout_head(os.path.relpath(TRACKED_DIR_FP_WITH_SPACE, DIR))
    os.chdir(DIR)
    self.__assert_checkout_head(os.path.relpath(TRACKED_DIR_DIR_FP, DIR_DIR))
    self.__assert_checkout_head(
        os.path.relpath(TRACKED_DIR_DIR_FP_WITH_SPACE, DIR_DIR))


  def __assert_checkout_not_head(self, *fps):
    root = self.repo.root
    for fp in fps:
      utils_lib.write_file(fp, contents='contents')
      self.curr_b.checkout_file(
          os.path.relpath(fp, root), self.repo.revparse_single('HEAD^'))
      self.assertEqual(TRACKED_FP_CONTENTS_1, utils_lib.read_file(fp))

  def test_checkout_not_head(self):
    self.__assert_checkout_not_head(
        TRACKED_FP, TRACKED_FP_WITH_SPACE,
        TRACKED_DIR_FP, TRACKED_DIR_FP_WITH_SPACE,
        TRACKED_DIR_DIR_FP, TRACKED_DIR_DIR_FP_WITH_SPACE)

  def test_checkout_not_head_relative(self):
    os.chdir(DIR)
    self.__assert_checkout_not_head(os.path.relpath(TRACKED_DIR_FP, DIR))
    self.__assert_checkout_not_head(
        os.path.relpath(TRACKED_DIR_FP_WITH_SPACE, DIR))
    os.chdir(DIR)
    self.__assert_checkout_not_head(
        os.path.relpath(TRACKED_DIR_DIR_FP, DIR_DIR))
    self.__assert_checkout_not_head(
        os.path.relpath(TRACKED_DIR_DIR_FP_WITH_SPACE, DIR_DIR))


  def __assert_checkout_error(self, *fps, **kwargs):
    root = self.repo.root
    cp = kwargs.get('cp', 'HEAD')
    for fp in fps:
      self.assertRaises(
          KeyError, self.curr_b.checkout_file, os.path.relpath(fp, root),
          self.repo.revparse_single(cp))

  @common.assert_no_side_effects(
      UNTRACKED_FP, UNTRACKED_FP_WITH_SPACE,
      UNTRACKED_DIR_FP, UNTRACKED_DIR_FP_WITH_SPACE,
      UNTRACKED_DIR_DIR_FP, UNTRACKED_DIR_DIR_FP_WITH_SPACE)
  def test_checkout_uncommitted(self):
    self.__assert_checkout_error(
        UNTRACKED_FP, UNTRACKED_FP_WITH_SPACE,
        UNTRACKED_DIR_FP, UNTRACKED_DIR_FP_WITH_SPACE,
        UNTRACKED_DIR_DIR_FP, UNTRACKED_DIR_DIR_FP_WITH_SPACE)
    self.__assert_checkout_error(
        UNTRACKED_FP, UNTRACKED_FP_WITH_SPACE,
        UNTRACKED_DIR_FP, UNTRACKED_DIR_FP_WITH_SPACE,
        UNTRACKED_DIR_DIR_FP, UNTRACKED_DIR_DIR_FP_WITH_SPACE, cp='HEAD^1')

  def test_checkout_nonexistent(self):
    self.__assert_checkout_error(NONEXISTENT_FP, NONEXISTENT_FP_WITH_SPACE)


class TestStatus(TestFile):

  def test_status_all(self):
    st_all = self.curr_b.status()

    # Some code is commented out because there's currently no way to get
    # status to repot ignored and tracked unmodified files

    #seen = []
    for fp, f_type, exists_at_head, exists_in_wd, modified, _ in st_all:
      #if (fp == TRACKED_FP or fp == TRACKED_FP_WITH_SPACE or
      #    fp == TRACKED_DIR_FP or fp == TRACKED_DIR_FP_WITH_SPACE or
      #    fp == TRACKED_DIR_DIR_FP or fp == TRACKED_DIR_DIR_FP_WITH_SPACE):
      #  self.__assert_type(fp, core.GL_STATUS_TRACKED, f_type)
      #  self.__assert_field(fp, 'exists_at_head', True, exists_at_head)
      #  self.__assert_field(fp, 'modified', False, modified)
      if (fp == UNTRACKED_FP or fp == UNTRACKED_FP_WITH_SPACE or
            fp == UNTRACKED_DIR_FP or fp == UNTRACKED_DIR_FP_WITH_SPACE or
            fp == UNTRACKED_DIR_DIR_FP or
            fp == UNTRACKED_DIR_DIR_FP_WITH_SPACE):
        self.__assert_type(fp, core.GL_STATUS_UNTRACKED, f_type)
        self.__assert_field(fp, 'exists_at_head', False, exists_at_head)
        self.__assert_field(fp, 'modified', True, modified)
      #elif fp == IGNORED_FP or fp == IGNORED_FP_WITH_SPACE:
      #  self.__assert_type(fp, core.GL_STATUS_IGNORED, f_type)
      #  self.__assert_field(fp, 'exists_at_head', False, exists_at_head)
      #  self.__assert_field(fp, 'modified', True, modified)
      elif fp == '.gitignore':
        self.__assert_type(fp, core.GL_STATUS_UNTRACKED, f_type)
        self.__assert_field(fp, 'exists_at_head', False, exists_at_head)
        self.__assert_field(fp, 'modified', True, modified)
      #else:
      #  self.fail('Unexpected fp {0}'.format(fp))
      self.__assert_field(fp, 'exists_in_wd', True, exists_in_wd)
      #seen.append(fp)
    #self.assertItemsEqual(seen, ALL_FPS_IN_WD)

  def test_status_equivalence(self):
    for f_st in self.curr_b.status():
      self.assertEqual(f_st, self.curr_b.status_file(f_st.fp))

  def test_status_nonexistent_fp(self):
    self.assertRaises(KeyError, self.curr_b.status_file, NONEXISTENT_FP)
    self.assertRaises(
        KeyError, self.curr_b.status_file, NONEXISTENT_FP_WITH_SPACE)

  def test_status_modify(self):
    utils_lib.write_file(TRACKED_FP, contents='contents')
    st = self.curr_b.status_file(TRACKED_FP)
    self.assertTrue(st.modified)
    utils_lib.write_file(TRACKED_FP, contents=TRACKED_FP_CONTENTS_2)
    st = self.curr_b.status_file(TRACKED_FP)
    self.assertFalse(st.modified)

  def test_status_rm(self):
    os.remove(TRACKED_FP)
    st = self.curr_b.status_file(TRACKED_FP)
    self.assertEqual(core.GL_STATUS_TRACKED, st.type)
    self.assertTrue(st.modified)
    self.assertTrue(st.exists_at_head)
    self.assertFalse(st.exists_in_wd)

    utils_lib.write_file(TRACKED_FP, contents=TRACKED_FP_CONTENTS_2)
    st = self.curr_b.status_file(TRACKED_FP)
    self.assertEqual(core.GL_STATUS_TRACKED, st.type)
    self.assertFalse(st.modified)
    self.assertTrue(st.exists_at_head)
    self.assertTrue(st.exists_in_wd)

  def test_status_track_rm(self):
    self.curr_b.track_file(UNTRACKED_FP)
    st = self.curr_b.status_file(UNTRACKED_FP)
    self.assertEqual(core.GL_STATUS_TRACKED, st.type)
    self.assertTrue(st.modified)

    os.remove(UNTRACKED_FP)
    self.assertRaises(KeyError, self.curr_b.status_file, UNTRACKED_FP)

  def test_status_track_untrack(self):
    self.curr_b.track_file(UNTRACKED_FP)
    st = self.curr_b.status_file(UNTRACKED_FP)
    self.assertEqual(core.GL_STATUS_TRACKED, st.type)
    self.assertTrue(st.modified)

    self.curr_b.untrack_file(UNTRACKED_FP)
    st = self.curr_b.status_file(UNTRACKED_FP)
    self.assertEqual(core.GL_STATUS_UNTRACKED, st.type)
    self.assertTrue(st.modified)

  def test_status_unignore(self):
    utils_lib.write_file('.gitignore', contents='')
    st = self.curr_b.status_file(IGNORED_FP)
    self.assertEqual(core.GL_STATUS_UNTRACKED, st.type)

    st = self.curr_b.status_file(IGNORED_FP_WITH_SPACE)
    self.assertEqual(core.GL_STATUS_UNTRACKED, st.type)

  def test_status_ignore(self):
    contents = utils_lib.read_file('.gitignore') + '\n' + TRACKED_FP
    utils_lib.write_file('.gitignore', contents=contents)
    # Tracked files can't be ignored.
    st = self.curr_b.status_file(TRACKED_FP)
    self.assertEqual(core.GL_STATUS_TRACKED, st.type)

  def test_status_untrack_tracked_modify(self):
    self.curr_b.untrack_file(TRACKED_FP)
    st = self.curr_b.status_file(TRACKED_FP)
    self.assertEqual(core.GL_STATUS_UNTRACKED, st.type)
    # self.assertFalse(st.modified)

    utils_lib.write_file(TRACKED_FP, contents='contents')
    st = self.curr_b.status_file(TRACKED_FP)
    self.assertEqual(core.GL_STATUS_UNTRACKED, st.type)
    self.assertTrue(st.modified)

  def test_status_untrack_tracked_rm(self):
    self.curr_b.untrack_file(TRACKED_FP)
    st = self.curr_b.status_file(TRACKED_FP)
    self.assertEqual(core.GL_STATUS_UNTRACKED, st.type)

    os.remove(TRACKED_FP)
    st = self.curr_b.status_file(TRACKED_FP)
    self.assertEqual(core.GL_STATUS_UNTRACKED, st.type)
    self.assertTrue(st.modified)
    self.assertFalse(st.exists_in_wd)
    self.assertTrue(st.exists_at_head)

  def test_status_ignore_tracked(self):
    """Assert that ignoring a tracked file has no effect."""
    utils_lib.append_to_file('.gitignore', contents='\n' + TRACKED_FP + '\n')
    st = self.curr_b.status_file(TRACKED_FP)
    self.__assert_type(TRACKED_FP, core.GL_STATUS_TRACKED, st.type)

  def test_status_ignore_untracked(self):
    """Assert that ignoring a untracked file makes it ignored."""
    utils_lib.append_to_file('.gitignore', contents='\n' + UNTRACKED_FP + '\n')
    st = self.curr_b.status_file(UNTRACKED_FP)
    self.__assert_type(UNTRACKED_FP, core.GL_STATUS_IGNORED, st.type)


  def __assert_type(self, fp, expected, got):
    self.assertEqual(
        expected, got,
        'Incorrect type for {0}: expected {1}, got {2}'.format(
            fp, expected, got))

  def __assert_field(self, fp, field, expected, got):
    self.assertEqual(
        expected, got,
        'Incorrect status for {0}: expected {1}={2}, got {3}={4}'.format(
            fp, field, expected, field, got))


class TestDiffFile(TestFile):

  # TODO(sperezde): add DIR, DIR_DIR, relative tests to diff.

  @common.assert_status_unchanged(
      UNTRACKED_FP, UNTRACKED_FP_WITH_SPACE,
      IGNORED_FP, IGNORED_FP_WITH_SPACE)
  def test_diff_nontracked(self):
    fps = [
        UNTRACKED_FP, UNTRACKED_FP_WITH_SPACE,
        IGNORED_FP, IGNORED_FP_WITH_SPACE]
    for fp in fps:
      utils_lib.write_file(fp, contents='new contents')
      patch = self.curr_b.diff_file(fp)

      self.assertEqual(1, patch.additions)
      self.assertEqual(0, patch.deletions)

      self.assertEqual(1, len(patch.hunks))
      hunk = list(patch.hunks)[0]
      lines = list(hunk.lines)

      self.assertEqual(2, len(lines))
      self.assertEqual('+', lines[0][0])
      self.assertEqual('new contents', lines[0][1])

  def test_diff_nonexistent_fp(self):
    self.assertRaises(KeyError, self.curr_b.diff_file, NONEXISTENT_FP)
    self.assertRaises(
        KeyError, self.curr_b.diff_file, NONEXISTENT_FP_WITH_SPACE)

  @common.assert_no_side_effects(TRACKED_FP)
  def test_empty_diff(self):
    patch = self.curr_b.diff_file(TRACKED_FP)
    self.assertEqual(0, len(list(patch.hunks)))
    self.assertEqual(0, patch.additions)
    self.assertEqual(0, patch.deletions)

  def test_diff_basic(self):
    utils_lib.write_file(TRACKED_FP, contents='new contents')
    patch = self.curr_b.diff_file(TRACKED_FP)

    self.assertEqual(1, patch.additions)
    self.assertEqual(1, patch.deletions)

    self.assertEqual(1, len(patch.hunks))
    hunk = list(patch.hunks)[0]
    lines = list(hunk.lines)

    self.assertEqual(3, len(lines))
    self.assertEqual('-', lines[0][0])
    self.assertEqual(TRACKED_FP_CONTENTS_2, lines[0][1])

    self.assertEqual('+', lines[1][0])
    self.assertEqual('new contents', lines[1][1])

  def test_diff_append(self):
    utils_lib.append_to_file(TRACKED_FP, contents='new contents')
    patch = self.curr_b.diff_file(TRACKED_FP)

    self.assertEqual(1, patch.additions)
    self.assertEqual(0, patch.deletions)

    self.assertEqual(1, len(patch.hunks))
    hunk = list(patch.hunks)[0]
    lines = list(hunk.lines)

    self.assertEqual(3, len(lines))
    self.assertEqual(' ', lines[0][0])
    self.assertEqual(TRACKED_FP_CONTENTS_2, lines[0][1])

    self.assertEqual('+', lines[1][0])
    self.assertEqual('new contents', lines[1][1])

  def test_diff_new_fp(self):
    fp = 'new'
    new_fp_contents = 'new fp contents\n'
    utils_lib.write_file(fp, contents=new_fp_contents)
    self.curr_b.track_file(fp)
    patch = self.curr_b.diff_file(fp)

    self.assertEqual(1, patch.additions)
    self.assertEqual(0, patch.deletions)

    self.assertEqual(1, len(patch.hunks))
    hunk = list(patch.hunks)[0]
    lines = list(hunk.lines)

    self.assertEqual(1, len(lines))
    self.assertEqual('+', lines[0][0])
    self.assertEqual(new_fp_contents, lines[0][1])

    # Now let's add some change to the file and check that diff notices it.
    utils_lib.append_to_file(fp, contents='new line')
    patch = self.curr_b.diff_file(fp)

    self.assertEqual(2, patch.additions)
    self.assertEqual(0, patch.deletions)

    self.assertEqual(1, len(patch.hunks))
    hunk = list(patch.hunks)[0]
    lines = list(hunk.lines)

    self.assertEqual(3, len(lines))
    self.assertEqual('+', lines[0][0])
    self.assertEqual(new_fp_contents, lines[0][1])

    self.assertEqual('+', lines[1][0])
    self.assertEqual('new line', lines[1][1])


FP_IN_CONFLICT = 'f_conflict'
DIR_FP_IN_CONFLICT = os.path.join(DIR, FP_IN_CONFLICT)


class TestResolveFile(TestFile):

  def setUp(self):
    super(TestResolveFile, self).setUp()

    # Generate a conflict.
    utils_lib.git_call('checkout -b branch')
    utils_lib.write_file(FP_IN_CONFLICT, contents='branch')
    utils_lib.write_file(DIR_FP_IN_CONFLICT, contents='branch')
    utils_lib.git_call(
        'add "{0}" "{1}"'.format(FP_IN_CONFLICT, DIR_FP_IN_CONFLICT))
    utils_lib.git_call(
        'commit -m"branch" "{0}" "{1}"'.format(
            FP_IN_CONFLICT, DIR_FP_IN_CONFLICT))
    utils_lib.git_call('checkout master')
    utils_lib.write_file(FP_IN_CONFLICT, contents='master')
    utils_lib.write_file(DIR_FP_IN_CONFLICT, contents='master')
    utils_lib.git_call(
        'add "{0}" "{1}"'.format(FP_IN_CONFLICT, DIR_FP_IN_CONFLICT))
    utils_lib.git_call(
        'commit -m"master" "{0}" "{1}"'.format(
            FP_IN_CONFLICT, DIR_FP_IN_CONFLICT))
    utils_lib.git_call('merge branch', expected_ret_code=1)

  @common.assert_no_side_effects(TRACKED_FP)
  def test_resolve_fp_with_no_conflicts(self):
    self.assertRaisesRegexp(
        ValueError, 'no conflicts', self.curr_b.resolve_file, TRACKED_FP)


  def __assert_resolve_fp(self, *fps):
    for fp in fps:
      self.curr_b.resolve_file(fp)
      st = self.curr_b.status_file(fp)
      self.assertFalse(st.in_conflict)

  @common.assert_contents_unchanged(FP_IN_CONFLICT, DIR_FP_IN_CONFLICT)
  def test_resolve_fp_with_conflicts(self):
    self.__assert_resolve_fp(FP_IN_CONFLICT, DIR_FP_IN_CONFLICT)


  def test_resolve_relative(self):
    self.__assert_resolve_fp(DIR_FP_IN_CONFLICT)
    os.chdir(DIR)
    st = self.curr_b.status_file(DIR_FP_IN_CONFLICT)
    self.assertFalse(st.in_conflict)
    self.assertRaisesRegexp(
        ValueError, 'no conflicts',
        self.curr_b.resolve_file, DIR_FP_IN_CONFLICT)
