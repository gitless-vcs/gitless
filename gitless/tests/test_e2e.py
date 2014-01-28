# Gitless - a version control system built on top of Git.
# Copyright (c) 2013  Santiago Perez De Rosso.
# Licensed under GNU GPL, version 2.

"""End-to-end test."""


import logging
import time
import unittest

import gitless.tests.utils as utils_lib


class TestEndToEnd(utils_lib.TestBase):

  def setUp(self):
    super(TestEndToEnd, self).setUp('gl-e2e-test')

  # TODO(sperezde): add dialog related tests.
  # TODO(sperezde): add checkout related tests.

  def test_basic_functionality(self):
    utils_lib.gl_expect_success('init')
    utils_lib.set_test_config()
    utils_lib.write_file('file1', 'Contents of file1')
    # Track.
    utils_lib.gl_expect_success('track file1')
    utils_lib.gl_expect_error('track file1')  # file1 is already tracked.
    utils_lib.gl_expect_error('track non-existent')
    # Untrack.
    utils_lib.gl_expect_success('untrack file1')
    utils_lib.gl_expect_success('untrack file1')  # file1 is already untracked.
    utils_lib.gl_expect_error('untrack non-existent')
    # Commit.
    utils_lib.gl_expect_success('commit -m"file1 commit"')
    utils_lib.gl_expect_error('commit -m"nothing to commit"')
    # History.
    if 'file1 commit' not in utils_lib.gl_expect_success('history')[0]:
      self.fail('Commit didn\'t appear in history')
    # Branch.
    # Make some changes in file1 and branch out.
    utils_lib.write_file('file1', 'New contents of file1')
    utils_lib.gl_expect_success('branch branch1')
    if 'New' in utils_lib.read_file('file1'):
      self.fail('Branch not independent!')
    # Switch back to master branch, check that contents are the same as before.
    utils_lib.gl_expect_success('branch master')
    if 'New' not in utils_lib.read_file('file1'):
      self.fail('Branch not independent!')
    out, _ = utils_lib.gl_expect_success('branch')
    if '* master' not in out:
      self.fail('Branch status output wrong')
    if 'branch1' not in out:
      self.fail('Branch status output wrong')

    utils_lib.gl_expect_success('branch branch1')
    utils_lib.gl_expect_success('branch branch2')
    utils_lib.gl_expect_success('branch branch-conflict1')
    utils_lib.gl_expect_success('branch branch-conflict2')
    utils_lib.gl_expect_success('branch master')
    utils_lib.gl_expect_success('commit -m"New contents commit"')

    # Rebase.
    utils_lib.gl_expect_success('branch branch1')
    utils_lib.gl_expect_error('rebase')  # no upstream set.
    utils_lib.gl_expect_success('rebase master')
    if 'file1 commit' not in utils_lib.gl_expect_success('history')[0]:
      self.fail()

    # Merge.
    utils_lib.gl_expect_success('branch branch2')
    utils_lib.gl_expect_error('merge')  # no upstream set.
    utils_lib.gl_expect_success('merge master')
    if 'file1 commit' not in utils_lib.gl_expect_success('history')[0]:
      self.fail()

    # Conflicting rebase.
    utils_lib.gl_expect_success('branch branch-conflict1')
    utils_lib.write_file('file1', 'Conflicting changes to file1')
    utils_lib.gl_expect_success('commit -m"changes in branch-conflict1"')
    if 'conflict' not in utils_lib.gl_expect_error('rebase master')[1]:
      self.fail()
    if 'file1 (with conflicts)' not in utils_lib.gl_expect_success('status')[0]:
      self.fail()
    utils_lib.write_file('file1', 'Fixed conflicts!')
    utils_lib.gl_expect_error('commit -m"shouldn\'t work (resolve not called)"')
    utils_lib.gl_expect_success('resolve file1')
    utils_lib.gl_expect_success('commit -m"fixed conflicts"')

  # TODO(sperezde): add more performance tests to check that we're not dropping
  # the ball: We should try to keep Gitless's performance reasonably close to
  # Git's.

  def test_status_performance(self):
    """Assert that gl status is not too slow."""

    def assert_status_performance():
      # The test fails if gl status takes more than 100 times
      # the time git status took.
      MAX_TOLERANCE = 100

      t = time.time()
      utils_lib.gl_call('status')
      gl_t = time.time() - t

      t = time.time()
      utils_lib.git_call('status')
      git_t = time.time() - t

      self.assertTrue(
          gl_t < git_t*MAX_TOLERANCE,
          msg='gl_t {0}, git_t {1}'.format(gl_t, git_t))

    self.__build_repo()
    # All files are untracked.
    assert_status_performance()
    # Track all files, repeat.
    logging.info('Doing a massive git add, this might take a while')
    utils_lib.git_call('add .')
    logging.info('Done')
    assert_status_performance()

  def test_branch_switch_performance(self):
    """Assert that switching branches is not too slow."""
    MAX_TOLERANCE = 100

    self.__build_repo()
    # Temporary hack until we get stuff working smoothly when the repo has no
    # commits.
    utils_lib.gl_call('commit -m"commit" f1')

    t = time.time()
    utils_lib.gl_call('branch develop')
    gl_t = time.time() - t

    # go back to previous state.
    utils_lib.gl_call('branch master')

    # do the same for git.
    t = time.time()
    utils_lib.git_call('branch gitdev')
    utils_lib.git_call('stash save --all')
    utils_lib.git_call('checkout gitdev')
    git_t = time.time() - t

    self.assertTrue(
        gl_t < git_t*MAX_TOLERANCE,
        msg='gl_t {0}, git_t {1}'.format(gl_t, git_t))

  def __build_repo(self, fps_qty=10000):
    for i in range(0, fps_qty):
      fp = 'f' + str(i)
      utils_lib.write_file(fp, fp)

    utils_lib.gl_call('init')
    utils_lib.set_test_config()


if __name__ == '__main__':
  unittest.main()
