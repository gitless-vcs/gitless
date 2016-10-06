# -*- coding: utf-8 -*-
# Gitless - a version control system built on top of Git
# Licensed under GNU GPL v2

"""Core unit tests."""


from __future__ import unicode_literals

from functools import wraps
import os
import shutil
import tempfile

from sh import git

from gitless import core
import gitless.tests.utils as utils_lib


TRACKED_FP = 'f1'
TRACKED_FP_CONTENTS_1 = 'f1-1\n'
TRACKED_FP_CONTENTS_2 = 'f1-2\n'
TRACKED_FP_WITH_SPACE = 'f1 space'
UNTRACKED_FP = 'f2'
UNTRACKED_FP_CONTENTS = 'f2'
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
BRANCH = 'b1'
REMOTE_BRANCH = 'rb'
FP_IN_CONFLICT = 'f_conflict'
DIR_FP_IN_CONFLICT = os.path.join(DIR, FP_IN_CONFLICT)


# Helpers

class TestCore(utils_lib.TestBase):
  """Base class for core tests."""

  def setUp(self):
    super(TestCore, self).setUp('gl-core-test')
    git.init()
    utils_lib.set_test_config()
    self.repo = core.Repository()


def assert_contents_unchanged(*fps):
  """Decorator that fails the test if the contents of the file fp changed."""
  def prop(*args, **kwargs):
    return utils_lib.read_file
  return __assert_decorator('Contents', prop, *fps)


def assert_status_unchanged(*fps):
  """Decorator that fails the test if the status of fp changed."""
  def prop(self, *args, **kwargs):
    return self.curr_b.status_file
  return __assert_decorator('Status', prop, *fps)


def assert_no_side_effects(*fps):
  """Decorator that fails the test if the contents or status of fp changed."""
  def decorator(f):
    @assert_contents_unchanged(*fps)
    @assert_status_unchanged(*fps)
    @wraps(f)
    def wrapper(*args, **kwargs):
      f(*args, **kwargs)
    return wrapper
  return decorator


def __assert_decorator(msg, prop, *fps):
  def decorator(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
      self = args[0]
      # We save up the cwd to chdir to it after the test has run so that the
      # the given fps still "work" even if the test changed the cwd.
      cwd_before = os.getcwd()
      before_list = [prop(*args, **kwargs)(fp) for fp in fps]
      f(*args, **kwargs)
      os.chdir(cwd_before)
      after_list = [prop(*args, **kwargs)(fp) for fp in fps]
      for fp, before, after in zip(fps, before_list, after_list):
        self.assertEqual(
            before, after,
            '{0} of file "{1}" changed: from "{2}" to "{3}"'.format(
                msg, fp, before, after))
    return wrapper
  return decorator


# Unit tests for file related operations

class TestFile(TestCore):
  """Base class for file tests."""

  def setUp(self):
    super(TestFile, self).setUp()

    # Build up an interesting mock repo
    utils_lib.write_file(TRACKED_FP, contents=TRACKED_FP_CONTENTS_1)
    utils_lib.write_file(TRACKED_FP_WITH_SPACE, contents=TRACKED_FP_CONTENTS_1)
    utils_lib.write_file(TRACKED_DIR_FP, contents=TRACKED_FP_CONTENTS_1)
    utils_lib.write_file(
        TRACKED_DIR_FP_WITH_SPACE, contents=TRACKED_FP_CONTENTS_1)
    utils_lib.write_file(TRACKED_DIR_DIR_FP, contents=TRACKED_FP_CONTENTS_1)
    utils_lib.write_file(
        TRACKED_DIR_DIR_FP_WITH_SPACE, contents=TRACKED_FP_CONTENTS_1)
    git.add(
        TRACKED_FP, TRACKED_FP_WITH_SPACE,
        TRACKED_DIR_FP, TRACKED_DIR_FP_WITH_SPACE,
        TRACKED_DIR_DIR_FP, TRACKED_DIR_DIR_FP_WITH_SPACE)
    git.commit(
        TRACKED_FP, TRACKED_FP_WITH_SPACE,
        TRACKED_DIR_FP, TRACKED_DIR_FP_WITH_SPACE,
        TRACKED_DIR_DIR_FP, TRACKED_DIR_DIR_FP_WITH_SPACE, m='1')
    utils_lib.write_file(TRACKED_FP, contents=TRACKED_FP_CONTENTS_2)
    utils_lib.write_file(TRACKED_FP_WITH_SPACE, contents=TRACKED_FP_CONTENTS_2)
    utils_lib.write_file(TRACKED_DIR_FP, contents=TRACKED_FP_CONTENTS_2)
    utils_lib.write_file(
        TRACKED_DIR_FP_WITH_SPACE, contents=TRACKED_FP_CONTENTS_2)
    utils_lib.write_file(TRACKED_DIR_DIR_FP, contents=TRACKED_FP_CONTENTS_2)
    utils_lib.write_file(
        TRACKED_DIR_DIR_FP_WITH_SPACE, contents=TRACKED_FP_CONTENTS_2)
    git.commit(
        TRACKED_FP, TRACKED_FP_WITH_SPACE,
        TRACKED_DIR_FP, TRACKED_DIR_FP_WITH_SPACE,
        TRACKED_DIR_DIR_FP, TRACKED_DIR_DIR_FP_WITH_SPACE, m='2')
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


class TestFileTrack(TestFile):

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

  @assert_contents_unchanged(
      UNTRACKED_FP, UNTRACKED_FP_WITH_SPACE,
      UNTRACKED_DIR_FP, UNTRACKED_DIR_FP_WITH_SPACE,
      UNTRACKED_DIR_DIR_FP, UNTRACKED_DIR_DIR_FP_WITH_SPACE)
  def test_track_untracked(self):
    self.__assert_track_untracked(
        UNTRACKED_FP, UNTRACKED_FP_WITH_SPACE,
        UNTRACKED_DIR_FP, UNTRACKED_DIR_FP_WITH_SPACE,
        UNTRACKED_DIR_DIR_FP, UNTRACKED_DIR_DIR_FP_WITH_SPACE)

  @assert_contents_unchanged(
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

  @assert_no_side_effects(
      TRACKED_FP, TRACKED_FP_WITH_SPACE,
      TRACKED_DIR_FP, TRACKED_DIR_FP_WITH_SPACE,
      TRACKED_DIR_DIR_FP, TRACKED_DIR_DIR_FP_WITH_SPACE)
  def test_track_tracked_fp(self):
    self.__assert_track_tracked(
        TRACKED_FP, TRACKED_FP_WITH_SPACE,
        TRACKED_DIR_FP, TRACKED_DIR_FP_WITH_SPACE,
        TRACKED_DIR_DIR_FP, TRACKED_DIR_DIR_FP_WITH_SPACE)

  @assert_no_side_effects(
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

  @assert_no_side_effects(IGNORED_FP, IGNORED_FP_WITH_SPACE)
  def test_track_ignored(self):
    self.__assert_track_ignored(IGNORED_FP, IGNORED_FP_WITH_SPACE)


class TestFileUntrack(TestFile):

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

  @assert_contents_unchanged(
      TRACKED_FP, TRACKED_FP_WITH_SPACE,
      TRACKED_DIR_FP, TRACKED_DIR_FP_WITH_SPACE,
      TRACKED_DIR_DIR_FP, TRACKED_DIR_DIR_FP_WITH_SPACE)
  def test_untrack_tracked(self):
    self.__assert_untrack_tracked(
        TRACKED_FP, TRACKED_FP_WITH_SPACE,
        TRACKED_DIR_FP, TRACKED_DIR_FP_WITH_SPACE,
        TRACKED_DIR_DIR_FP, TRACKED_DIR_DIR_FP_WITH_SPACE)

  @assert_contents_unchanged(
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

  @assert_no_side_effects(
      UNTRACKED_FP, UNTRACKED_FP_WITH_SPACE,
      UNTRACKED_DIR_FP, UNTRACKED_DIR_FP_WITH_SPACE,
      UNTRACKED_DIR_DIR_FP, UNTRACKED_DIR_DIR_FP_WITH_SPACE)
  def test_untrack_untracked_fp(self):
    self.__assert_untrack_untracked(
        UNTRACKED_FP, UNTRACKED_FP_WITH_SPACE,
        UNTRACKED_DIR_FP, UNTRACKED_DIR_FP_WITH_SPACE,
        UNTRACKED_DIR_DIR_FP, UNTRACKED_DIR_DIR_FP_WITH_SPACE)

  @assert_contents_unchanged(
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

  @assert_no_side_effects(IGNORED_FP, IGNORED_FP_WITH_SPACE)
  def test_untrack_ignored(self):
    self.__assert_untrack_ignored(IGNORED_FP, IGNORED_FP_WITH_SPACE)


class TestFileCheckout(TestFile):

  def __assert_checkout_head(self, *fps):
    root = self.repo.root
    for fp in fps:
      utils_lib.write_file(fp, contents='contents')
      self.curr_b.checkout_file(
          os.path.relpath(fp, root), self.repo.revparse_single('HEAD'))
      self.assertEqual(TRACKED_FP_CONTENTS_2, utils_lib.read_file(fp))

  @assert_no_side_effects(
      TRACKED_FP, TRACKED_FP_WITH_SPACE,
      TRACKED_DIR_FP, TRACKED_DIR_FP_WITH_SPACE,
      TRACKED_DIR_DIR_FP, TRACKED_DIR_DIR_FP_WITH_SPACE)
  def test_checkout_head(self):
    self.__assert_checkout_head(
        TRACKED_FP, TRACKED_FP_WITH_SPACE,
        TRACKED_DIR_FP, TRACKED_DIR_FP_WITH_SPACE,
        TRACKED_DIR_DIR_FP, TRACKED_DIR_DIR_FP_WITH_SPACE)

  @assert_no_side_effects(
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

  @assert_no_side_effects(
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


class TestFileStatus(TestFile):

  def test_status_all(self):
    st_all = self.curr_b.status()
    for fp, f_type, exists_at_head, exists_in_wd, modified, _ in st_all:
      if (fp == UNTRACKED_FP or fp == UNTRACKED_FP_WITH_SPACE or
            fp == UNTRACKED_DIR_FP or fp == UNTRACKED_DIR_FP_WITH_SPACE or
            fp == UNTRACKED_DIR_DIR_FP or
            fp == UNTRACKED_DIR_DIR_FP_WITH_SPACE):
        self.__assert_type(fp, core.GL_STATUS_UNTRACKED, f_type)
        self.__assert_field(fp, 'exists_at_head', False, exists_at_head)
        self.__assert_field(fp, 'modified', True, modified)
      elif fp == '.gitignore':
        self.__assert_type(fp, core.GL_STATUS_UNTRACKED, f_type)
        self.__assert_field(fp, 'exists_at_head', False, exists_at_head)
        self.__assert_field(fp, 'modified', True, modified)
      self.__assert_field(fp, 'exists_in_wd', True, exists_in_wd)

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
    # Tracked files can't be ignored
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


class TestFileDiff(TestFile):

  @assert_status_unchanged(
      UNTRACKED_FP, UNTRACKED_FP_WITH_SPACE,
      IGNORED_FP, IGNORED_FP_WITH_SPACE)
  def test_diff_nontracked(self):
    fps = [
        UNTRACKED_FP, UNTRACKED_FP_WITH_SPACE,
        IGNORED_FP, IGNORED_FP_WITH_SPACE]
    for fp in fps:
      utils_lib.write_file(fp, contents='new contents')
      patch = self.curr_b.diff_file(fp)

      self.assertEqual(1, patch.line_stats[1])
      self.assertEqual(0, patch.line_stats[2])

      self.assertEqual(1, len(patch.hunks))
      hunk = list(patch.hunks)[0]

      self.assertEqual(2, len(hunk.lines))
      self.assertEqual('+', hunk.lines[0].origin)
      self.assertEqual('new contents', hunk.lines[0].content)

  def test_diff_nonexistent_fp(self):
    self.assertRaises(KeyError, self.curr_b.diff_file, NONEXISTENT_FP)
    self.assertRaises(
        KeyError, self.curr_b.diff_file, NONEXISTENT_FP_WITH_SPACE)

  @assert_no_side_effects(TRACKED_FP)
  def test_empty_diff(self):
    patch = self.curr_b.diff_file(TRACKED_FP)
    self.assertEqual(0, len(list(patch.hunks)))
    self.assertEqual(0, patch.line_stats[1])
    self.assertEqual(0, patch.line_stats[2])

  def test_diff_basic(self):
    utils_lib.write_file(TRACKED_FP, contents='new contents')
    patch = self.curr_b.diff_file(TRACKED_FP)

    self.assertEqual(1, patch.line_stats[1])
    self.assertEqual(1, patch.line_stats[2])

    self.assertEqual(1, len(patch.hunks))
    hunk = list(patch.hunks)[0]

    self.assertEqual(3, len(hunk.lines))
    self.assertEqual('-', hunk.lines[0].origin)
    self.assertEqual(TRACKED_FP_CONTENTS_2, hunk.lines[0].content)

    self.assertEqual('+', hunk.lines[1].origin)
    self.assertEqual('new contents', hunk.lines[1].content)

  def test_diff_append(self):
    utils_lib.append_to_file(TRACKED_FP, contents='new contents')
    patch = self.curr_b.diff_file(TRACKED_FP)

    self.assertEqual(1, patch.line_stats[1])
    self.assertEqual(0, patch.line_stats[2])

    self.assertEqual(1, len(patch.hunks))
    hunk = list(patch.hunks)[0]

    self.assertEqual(3, len(hunk.lines))
    self.assertEqual(' ', hunk.lines[0].origin)
    self.assertEqual(TRACKED_FP_CONTENTS_2, hunk.lines[0].content)

    self.assertEqual('+', hunk.lines[1].origin)
    self.assertEqual('new contents', hunk.lines[1].content)

  def test_diff_new_fp(self):
    fp = 'new'
    new_fp_contents = 'new fp contents\n'
    utils_lib.write_file(fp, contents=new_fp_contents)
    self.curr_b.track_file(fp)
    patch = self.curr_b.diff_file(fp)

    self.assertEqual(1, patch.line_stats[1])
    self.assertEqual(0, patch.line_stats[2])

    self.assertEqual(1, len(patch.hunks))
    hunk = list(patch.hunks)[0]

    self.assertEqual(1, len(hunk.lines))
    self.assertEqual('+', hunk.lines[0].origin)
    self.assertEqual(new_fp_contents, hunk.lines[0].content)

    # Now let's add some change to the file and check that diff notices it
    utils_lib.append_to_file(fp, contents='new line')
    patch = self.curr_b.diff_file(fp)

    self.assertEqual(2, patch.line_stats[1])
    self.assertEqual(0, patch.line_stats[2])

    self.assertEqual(1, len(patch.hunks))
    hunk = list(patch.hunks)[0]

    self.assertEqual(3, len(hunk.lines))
    self.assertEqual('+', hunk.lines[0].origin)
    self.assertEqual(new_fp_contents, hunk.lines[0].content)

    self.assertEqual('+', hunk.lines[1].origin)
    self.assertEqual('new line', hunk.lines[1].content)

  def test_diff_non_ascii(self):
    fp = 'new'
    new_fp_contents = '’◕‿◕’©Ä☺’ಠ_ಠ’\n'
    utils_lib.write_file(fp, contents=new_fp_contents)
    self.curr_b.track_file(fp)
    patch = self.curr_b.diff_file(fp)

    self.assertEqual(1, patch.line_stats[1])
    self.assertEqual(0, patch.line_stats[2])

    self.assertEqual(1, len(patch.hunks))
    hunk = list(patch.hunks)[0]

    self.assertEqual(1, len(hunk.lines))
    self.assertEqual('+', hunk.lines[0].origin)
    self.assertEqual(new_fp_contents, hunk.lines[0].content)

    utils_lib.append_to_file(fp, contents='new line')
    patch = self.curr_b.diff_file(fp)

    self.assertEqual(2, patch.line_stats[1])
    self.assertEqual(0, patch.line_stats[2])

    self.assertEqual(1, len(patch.hunks))
    hunk = list(patch.hunks)[0]

    self.assertEqual(3, len(hunk.lines))
    self.assertEqual('+', hunk.lines[0].origin)
    self.assertEqual(new_fp_contents, hunk.lines[0].content)

    self.assertEqual('+', hunk.lines[1].origin)
    self.assertEqual('new line', hunk.lines[1].content)


class TestFileResolve(TestFile):

  def setUp(self):
    super(TestFileResolve, self).setUp()

    # Generate a conflict
    git.checkout(b='branch')
    utils_lib.write_file(FP_IN_CONFLICT, contents='branch')
    utils_lib.write_file(DIR_FP_IN_CONFLICT, contents='branch')
    git.add(FP_IN_CONFLICT, DIR_FP_IN_CONFLICT)
    git.commit(FP_IN_CONFLICT, DIR_FP_IN_CONFLICT, m='branch')
    git.checkout('master')
    utils_lib.write_file(FP_IN_CONFLICT, contents='master')
    utils_lib.write_file(DIR_FP_IN_CONFLICT, contents='master')
    git.add(FP_IN_CONFLICT, DIR_FP_IN_CONFLICT)
    git.commit(FP_IN_CONFLICT, DIR_FP_IN_CONFLICT, m='master')
    git.merge('branch', _ok_code=[1])

  @assert_no_side_effects(TRACKED_FP)
  def test_resolve_fp_with_no_conflicts(self):
    self.assertRaisesRegexp(
        ValueError, 'no conflicts', self.curr_b.resolve_file, TRACKED_FP)

  def __assert_resolve_fp(self, *fps):
    for fp in fps:
      self.curr_b.resolve_file(fp)
      st = self.curr_b.status_file(fp)
      self.assertFalse(st.in_conflict)

  @assert_contents_unchanged(FP_IN_CONFLICT, DIR_FP_IN_CONFLICT)
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


# Unit tests for branch related operations

class TestBranch(TestCore):
  """Base class for branch tests."""

  def setUp(self):
    super(TestBranch, self).setUp()

    # Build up an interesting mock repo.
    utils_lib.write_file(TRACKED_FP, contents=TRACKED_FP_CONTENTS_1)
    git.add(TRACKED_FP)
    git.commit(TRACKED_FP, m='1')
    utils_lib.write_file(TRACKED_FP, contents=TRACKED_FP_CONTENTS_2)
    git.commit(TRACKED_FP, m='2')
    utils_lib.write_file(UNTRACKED_FP, contents=UNTRACKED_FP_CONTENTS)
    utils_lib.write_file('.gitignore', contents='{0}'.format(IGNORED_FP))
    utils_lib.write_file(IGNORED_FP)
    git.branch(BRANCH)

    self.curr_b = self.repo.current_branch


class TestBranchCreate(TestBranch):

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


class TestBranchDelete(TestBranch):

  def test_delete(self):
    self.repo.lookup_branch(BRANCH).delete()
    self.assertRaises(
        core.BranchIsCurrentError,
        self.repo.lookup_branch('master').delete)


class TestBranchSwitch(TestBranch):

  def test_switch_contents_still_there_untrack_tracked(self):
    self.curr_b.untrack_file(TRACKED_FP)
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
    git.commit(TRACKED_FP, m='comment')
    self.repo.switch_current_branch(self.repo.lookup_branch(BRANCH))
    self.assertEqual(TRACKED_FP_CONTENTS_2, utils_lib.read_file(TRACKED_FP))
    self.repo.switch_current_branch(self.repo.lookup_branch('master'))
    self.assertEqual('commit', utils_lib.read_file(TRACKED_FP))

  def test_switch_file_classification_is_mantained(self):
    self.curr_b.untrack_file(TRACKED_FP)
    self.repo.switch_current_branch(self.repo.lookup_branch(BRANCH))
    st = self.curr_b.status_file(TRACKED_FP)
    self.assertTrue(st)
    self.assertEqual(core.GL_STATUS_TRACKED, st.type)
    self.repo.switch_current_branch(self.repo.lookup_branch('master'))
    st = self.curr_b.status_file(TRACKED_FP)
    self.assertTrue(st)
    self.assertEqual(core.GL_STATUS_UNTRACKED, st.type)

  def test_switch_with_hidden_files(self):
    hf = '.file'
    utils_lib.write_file(hf)
    self.repo.switch_current_branch(self.repo.lookup_branch(BRANCH))
    utils_lib.write_file(hf, contents='contents')
    self.repo.switch_current_branch(self.repo.lookup_branch('master'))
    self.assertEqual(hf, utils_lib.read_file(hf))
    self.repo.switch_current_branch(self.repo.lookup_branch(BRANCH))
    self.assertEqual('contents', utils_lib.read_file(hf))


# Unit tests for remote related operations

class TestRemote(TestCore):
  """Base class for remote tests."""

  def setUp(self):
    """Creates temporary local Git repo to use as the remote."""
    super(TestRemote, self).setUp()

    # Create a repo to use as the remote
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


class TestRemoteCreate(TestRemote):

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


class TestRemoteList(TestRemote):

  def test_list_all(self):
    self.remotes.create('remote1', self.remote_path)
    self.remotes.create('remote2', self.remote_path)
    self.assertItemsEqual(
        ['remote1', 'remote2'], [r.name for r in self.remotes])


class TestRemoteDelete(TestRemote):

  def test_delete(self):
    self.remotes.create('remote', self.remote_path)
    self.remotes.delete('remote')

  def test_delete_nonexistent(self):
    self.assertRaises(KeyError, self.remotes.delete, 'remote')
    self.remotes.create('remote', self.remote_path)
    self.remotes.delete('remote')
    self.assertRaises(KeyError, self.remotes.delete, 'remote')


class TestRemoteSync(TestRemote):

  def setUp(self):
    super(TestRemoteSync, self).setUp()

    utils_lib.write_file('foo', contents='foo')
    git.add('foo')
    git.commit('foo', m='msg')

    self.repo.remotes.create('remote', self.remote_path)
    self.remote = self.repo.remotes['remote']

  def test_sync_changes(self):
    master_head_before = self.remote.lookup_branch('master').head
    remote_branch = self.remote.lookup_branch(REMOTE_BRANCH)
    remote_branch_head_before = remote_branch.head

    current_b = self.repo.current_branch
    # It is not a ff so it should fail
    self.assertRaises(core.GlError, current_b.publish, remote_branch)
    # Get the changes
    git.rebase(remote_branch)
    # Retry (this time it should work)
    current_b.publish(remote_branch)

    self.assertItemsEqual(
        ['master', REMOTE_BRANCH], self.remote.listall_branches())
    self.assertEqual(
        master_head_before.id, self.remote.lookup_branch('master').head.id)

    self.assertNotEqual(
        remote_branch_head_before.id,
        remote_branch.head.id)
    self.assertEqual(current_b.head.id, remote_branch.head.id)
