# -*- coding: utf-8 -*-
# Gitless - a version control system built on top of Git.
# Licensed under GNU GPL v2.

"""End-to-end test."""


import logging
import time

from sh import ErrorReturnCode, gl, git

import gitless.tests.utils as utils_lib


class TestEndToEnd(utils_lib.TestBase):

  def setUp(self):
    super(TestEndToEnd, self).setUp('gl-e2e-test')
    gl.init()
    utils_lib.set_test_config()


class TestNotInRepo(utils_lib.TestBase):

  def setUp(self):
    super(TestNotInRepo, self).setUp('gl-e2e-test')

  def test_not_in_repo(self):
    def assert_not_in_repo(*cmds):
      for cmd in cmds:
        self.assertRaisesRegexp(ErrorReturnCode, 'not in a Gitless\'s repository', cmd)

    assert_not_in_repo(
      gl.status, gl.diff, gl.commit, gl.branch, gl.merge, gl.rebase, gl.remote,
      gl.publish, gl.history)


# TODO(sperezde): add dialog related tests.
# TODO(sperezde): add checkout related tests.


class TestBasic(TestEndToEnd):

  def test_basic_functionality(self):
    utils_lib.write_file('file1', 'Contents of file1')
    # Track
    gl.track('file1')
    self.assertRaises(ErrorReturnCode, gl.track, 'file1')
    self.assertRaises(ErrorReturnCode, gl.track, 'non-existent')
    # Untrack
    gl.untrack('file1')
    self.assertRaises(ErrorReturnCode, gl.untrack, 'file1')
    self.assertRaises(ErrorReturnCode, gl.untrack, 'non-existent')
    # Commit
    gl.track('file1')
    gl.commit(m='file1 commit')
    self.assertRaises(ErrorReturnCode, gl.commit, m='nothing to commit')
    # History
    if 'file1 commit' not in str(gl.history(_tty_out=False)):
      self.fail('Commit didn\'t appear in history')
    # Branch
    # Make some changes to file1 and branch out
    utils_lib.write_file('file1', 'New contents of file1')
    gl.branch(c='branch1')
    gl.switch('branch1')
    if 'New' in utils_lib.read_file('file1'):
      self.fail('Branch not independent!')
    # Switch back to master branch, check that contents are the same as before.
    gl.switch('master')
    if 'New' not in utils_lib.read_file('file1'):
      self.fail('Branch not independent!')
    out = str(gl.branch(_tty_out=False))
    if '* master' not in out:
      self.fail('Branch status output wrong: {0}'.format(out))
    if 'branch1' not in out:
      self.fail('Branch status output wrong: {0}'.format(out))

    gl.branch(c='branch2')
    gl.branch(c='branch-conflict1')
    gl.branch(c='branch-conflict2')
    gl.commit(m='New contents commit')

    # Rebase
    gl.switch('branch1')
    self.assertRaises(ErrorReturnCode, gl.rebase)  # no upstream set
    gl.rebase('master')
    if 'file1 commit' not in str(gl.history(_tty_out=False)):
      self.fail()

    # Merge
    gl.switch('branch2')
    self.assertRaises(ErrorReturnCode, gl.merge)  # no upstream set
    gl.merge('master')
    if 'file1 commit' not in str(gl.history(_tty_out=False)):
      self.fail()

    # Conflicting rebase
    gl.switch('branch-conflict1')
    utils_lib.write_file('file1', 'Conflicting changes to file1')
    gl.commit(m='changes in branch-conflict1')
    err = str(gl.rebase('master', _tty_out=False, _ok_code=[1]).stderr)
    if 'conflict' not in err:
      self.fail()
    if 'file1 (with conflicts)' not in str(gl.status(_tty_out=False)):
      self.fail()

    # Try aborting
    gl.rebase('--abort')
    if 'file1' in str(gl.status(_tty_out=False)):
      self.fail()

    # Ok, now let's fix the conflicts
    err = str(gl.rebase('master', _tty_out=False, _ok_code=[1]).stderr)
    if 'conflict' not in err:
      self.fail()
    if 'file1 (with conflicts)' not in str(gl.status(_tty_out=False)):
      self.fail()

    utils_lib.write_file('file1', 'Fixed conflicts!')
    self.assertRaises(ErrorReturnCode, gl.commit, m='resolve not called')
    self.assertRaises(ErrorReturnCode, gl.resolve, 'non-existent')
    gl.resolve('file1')
    gl.commit(m='fixed conflicts')


class TestCommit(TestEndToEnd):

  TRACKED_FP = 'file1'
  UNTRACKED_FP = 'file2'
  FPS = [TRACKED_FP, UNTRACKED_FP]

  def setUp(self):
    super(TestCommit, self).setUp()
    utils_lib.write_file(self.TRACKED_FP)
    utils_lib.write_file(self.UNTRACKED_FP)
    gl.track(self.TRACKED_FP)

  # Happy paths
  def test_commit(self):
    gl.commit(m='msg')
    self.__assert_commit(self.TRACKED_FP)

  def test_commit_only(self):
    gl.commit(self.TRACKED_FP, m='msg')
    self.__assert_commit(self.TRACKED_FP)

  def test_commit_only_untrack(self):
    gl.commit(self.UNTRACKED_FP, m='msg')
    self.__assert_commit(self.UNTRACKED_FP)

  def test_commit_include(self):
    gl.commit(m='msg', include=self.UNTRACKED_FP)
    self.__assert_commit(self.TRACKED_FP, self.UNTRACKED_FP)

  def test_commit_exclude_include(self):
    gl.commit(m='msg', include=self.UNTRACKED_FP, exclude=self.TRACKED_FP)
    self.__assert_commit(self.UNTRACKED_FP)

  # Error paths
  def test_commit_no_files(self):
    self.assertRaises(
        ErrorReturnCode, gl.commit, m='msg', exclude=self.TRACKED_FP)
    self.assertRaises(ErrorReturnCode, gl.commit, 'non-existent', m='msg')
    self.assertRaises(
        ErrorReturnCode, gl.commit, m='msg', exclude='non-existent')
    self.assertRaises(
        ErrorReturnCode, gl.commit, m='msg', include='non-existent')

# TODO: uncomment once commit accepts paths instead of only files
#  def test_commit_dir(self):
#    utils_lib.write_file('dir/f')
#     self.assertRaises(ErrorReturnCode, gl.commit, 'dir', m='msg')

  def __assert_commit(self, *expected_committed):
    st = str(gl.status(_tty_out=False))
    h = str(gl.history(v=True, _tty_out=False))
    for fp in expected_committed:
      if fp in st or fp not in h:
        self.fail('{0} was apparently not committed!'.format(fp))
    expected_not_committed = [
        fp for fp in self.FPS if fp not in expected_committed]
    for fp in expected_not_committed:
      if fp not in st or fp in h:
        self.fail('{0} was apparently committed!'.format(fp))


class TestBranch(TestEndToEnd):

  BRANCH_1 = 'branch1'
  BRANCH_2 = 'branch2'

  def setUp(self):
    super(TestBranch, self).setUp()
    utils_lib.write_file('f')
    gl.commit('f', m='commit')

  def test_create(self):
    gl.branch(c=self.BRANCH_1)
    self.assertRaises(ErrorReturnCode, gl.branch, c=self.BRANCH_1)
    self.assertRaises(ErrorReturnCode, gl.branch, c='evil*named*branch')
    if self.BRANCH_1 not in str(gl.branch(_tty_out=False)):
      self.fail()

  def test_remove(self):
    gl.branch(c=self.BRANCH_1)
    gl.switch(self.BRANCH_1)
    self.assertRaises(ErrorReturnCode, gl.branch, d=self.BRANCH_1, _in='y')
    gl.branch(c=self.BRANCH_2)
    gl.switch(self.BRANCH_2)
    gl.branch(d=self.BRANCH_1, _in='n')
    gl.branch(d=self.BRANCH_1, _in='y')
    if self.BRANCH_1 in str(gl.branch(_tty_out=False)):
      self.fail()

  def test_upstream(self):
    self.assertRaises(ErrorReturnCode, gl.branch, '-uu')
    self.assertRaises(ErrorReturnCode, gl.branch, '-su', 'non-existent')
    self.assertRaises(
        ErrorReturnCode, gl.branch, '-su', 'non-existent/non-existent')


class TestDiff(TestEndToEnd):

  TRACKED_FP = 't_fp'
  UNTRACKED_FP = 'u_fp'

  def setUp(self):
    super(TestDiff, self).setUp()
    utils_lib.write_file(self.TRACKED_FP)
    gl.commit(self.TRACKED_FP, m="commit")
    utils_lib.write_file(self.UNTRACKED_FP)

  def test_empty_diff(self):
    if 'Nothing to diff' not in str(gl.diff(_tty_out=False)):
      self.fail()

  def test_diff_nonexistent_fp(self):
    err = str(gl.diff('file', _ok_code=[1]).stderr)
    if 'non-existent' not in err:
      self.fail()

  def test_basic_diff(self):
    utils_lib.write_file(self.TRACKED_FP, contents='contents')
    out1 = str(gl.diff(_tty_out=False))
    if '+contents' not in out1:
      self.fail()
    out2 = str(gl.diff(self.TRACKED_FP, _tty_out=False))
    if '+contents' not in out2:
      self.fail()
    self.assertEqual(out1, out2)


class TestPerformance(TestEndToEnd):

  FPS_QTY = 10000

  def setUp(self):
    super(TestPerformance, self).setUp()
    for i in range(0, self.FPS_QTY):
      fp = 'f' + str(i)
      utils_lib.write_file(fp, fp)

  def test_status_performance(self):
    """Assert that gl status is not too slow."""

    def assert_status_performance():
      # The test fails if gl status takes more than 100 times
      # the time git status took.
      MAX_TOLERANCE = 100

      t = time.time()
      gl.status()
      gl_t = time.time() - t

      t = time.time()
      git.status()
      git_t = time.time() - t

      self.assertTrue(
          gl_t < git_t*MAX_TOLERANCE,
          msg='gl_t {0}, git_t {1}'.format(gl_t, git_t))

    # All files are untracked
    assert_status_performance()
    # Track all files, repeat
    logging.info('Doing a massive git add, this might take a while')
    git.add('.')
    logging.info('Done')
    assert_status_performance()

  def test_branch_switch_performance(self):
    """Assert that switching branches is not too slow."""
    MAX_TOLERANCE = 100

    gl.commit('f1', m='commit')

    t = time.time()
    gl.branch(c='develop')
    gl.switch('develop')
    gl_t = time.time() - t

    # go back to previous state
    gl.switch('master')

    # do the same for git
    t = time.time()
    git.branch('gitdev')
    git.stash.save('--all')
    git.checkout('gitdev')
    git_t = time.time() - t

    self.assertTrue(
        gl_t < git_t*MAX_TOLERANCE,
        msg='gl_t {0}, git_t {1}'.format(gl_t, git_t))
