# Gitless - a version control system built on top of Git.
# Copyright (c) 2013  Santiago Perez De Rosso.
# Licensed under GNU GPL, version 2.

"""End-to-end test."""


import logging
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest


class TestEndToEnd(unittest.TestCase):

  def setUp(self):
    # Create temporary dir and cd to it.
    # TODO(sperezde): get the logging level via flags.
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    self.path = tempfile.mkdtemp(prefix='gl-e2e-test')
    logging.debug('Created temporary directory %s', self.path)
    os.chdir(self.path)

  def tearDown(self):
    shutil.rmtree(self.path)
    logging.debug('Removed dir %s', self.path)

  def __gl_call(self, cmd, expected_ret_code=0):
    return self.__call('gl', cmd, expected_ret_code=expected_ret_code)

  def __git_call(self, cmd, expected_ret_code=0):
    return self.__call('git', cmd, expected_ret_code=expected_ret_code)

  def __call(self, cmd, subcmd, expected_ret_code=0):
    logging.debug('Calling {0} {1}'.format(cmd, subcmd))
    p = subprocess.Popen(
        '{0} {1}'.format(cmd, subcmd), stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, shell=True)
    out, err = p.communicate()
    if sys.version > "3":
      out = out.decode('utf-8')
      err = err.decode('utf-8')
    logging.debug('Out is \n{0}'.format(out))
    if err:
      logging.debug('Err is \n{0}'.format(err))
    if p.returncode != expected_ret_code:
      self.fail(
          'Obtained ret code {0} doesn\'t match the expected {1}.\nOut of the'
          'cmd was:\n{2}\nErr of the cmd was:\n{3}\n'.format(
              p.returncode, expected_ret_code, out, err))
    return out, err

  def __success(self, cmd):
    return self.__gl_call(cmd)

  def __failure(self, cmd):
    return self.__gl_call(cmd, expected_ret_code=1)

  def __write_file(self, name, contents):
    f = open(name, 'w')
    f.write(contents)
    f.close()

  def __read_file(self, name):
    f = open(name, 'r')
    ret = f.read()
    f.close()
    return ret

  def __set_test_config(self):
    self.__git_call('config user.name \"test\"')
    self.__git_call('config user.email \"test@test.com\"')

  # TODO(sperezde): add dialog related tests.
  # TODO(sperezde): add checkout related tests.

  def test_basic_functionality(self):
    self.__success('init')
    self.__set_test_config()
    self.__write_file('file1', 'Contents of file1')
    # Track.
    self.__success('track file1')
    self.__failure('track file1')  # file1 is already tracked.
    self.__failure('track non-existent')
    # Untrack.
    self.__success('untrack file1')
    self.__success('untrack file1')  # file1 is already untracked.
    self.__failure('untrack non-existent')
    # Commit.
    self.__success('commit -m"file1 commit"')
    self.__failure('commit -m"nothing to commit"')  # nothing to commit.
    # History.
    if 'file1 commit' not in self.__success('history')[0]:
      self.fail('Commit didn\'t appear in history')
    # Branch.
    # Make some changes in file1 and branch out.
    self.__write_file('file1', 'New contents of file1')
    self.__success('branch branch1')
    if 'New' in self.__read_file('file1'):
      self.fail('Branch not independent!')
    # Switch back to master branch, check that contents are the same as before.
    self.__success('branch master')
    if 'New' not in self.__read_file('file1'):
      self.fail('Branch not independent!')
    out, _ = self.__success('branch')
    if '* master' not in out:
      self.fail('Branch status output wrong')
    if 'branch1' not in out:
      self.fail('Branch status output wrong')

    self.__success('branch branch1')
    self.__success('branch branch2')
    self.__success('branch branch-conflict1')
    self.__success('branch branch-conflict2')
    self.__success('branch master')
    self.__success('commit -m"New contents commit"')

    # Rebase.
    self.__success('branch branch1')
    self.__failure('rebase')  # no upstream set.
    self.__success('rebase master')
    if 'file1 commit' not in self.__success('history')[0]:
      self.fail()

    # Merge.
    self.__success('branch branch2')
    self.__failure('merge')  # no upstream set.
    self.__success('merge master')
    if 'file1 commit' not in self.__success('history')[0]:
      self.fail()

    # Conflicting rebase.
    self.__success('branch branch-conflict1')
    self.__write_file('file1', 'Conflicting changes to file1')
    self.__success('commit -m"changes in branch-conflict1"')
    if 'conflict' not in self.__failure('rebase master')[1]:
      self.fail()
    if 'file1 (with conflicts)' not in self.__success('status')[0]:
      self.fail()
    self.__write_file('file1', 'Fixed conflicts!')
    self.__failure('commit -m"shouldn\'t work"')  # resolve not called.
    self.__success('resolve file1')
    self.__success('commit -m"fixed conflicts"')

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
      self.__gl_call('status')
      gl_t = time.time() - t

      t = time.time()
      self.__git_call('status')
      git_t = time.time() - t

      self.assertTrue(
          gl_t < git_t*MAX_TOLERANCE,
          msg='gl_t {0}, git_t {1}'.format(gl_t, git_t))

    self.__build_repo()
    # All files are untracked.
    assert_status_performance()
    # Track all files, repeat.
    logging.info('Doing a massive git add, this might take a while')
    self.__git_call('add .')
    logging.info('Done')
    assert_status_performance()

  def test_branch_switch_performance(self):
    """Assert that switching branches is not too slow."""
    MAX_TOLERANCE = 100

    self.__build_repo()
    # Temporary hack until we get stuff working smoothly when the repo has no
    # commits.
    self.__gl_call('commit -m"commit" f1')

    t = time.time()
    self.__gl_call('branch develop')
    gl_t = time.time() - t

    # go back to previous state.
    self.__gl_call('branch master')

    # do the same for git.
    t = time.time()
    self.__git_call('branch gitdev')
    self.__git_call('stash save --all')
    self.__git_call('checkout gitdev')
    git_t = time.time() - t

    self.assertTrue(
        gl_t < git_t*MAX_TOLERANCE,
        msg='gl_t {0}, git_t {1}'.format(gl_t, git_t))

  def __build_repo(self, fps_qty=10000):
    for i in range(0, fps_qty):
      fp = 'f' + str(i)
      self.__write_file(fp, fp)

    self.__gl_call('init')
    self.__set_test_config()


if __name__ == '__main__':
  unittest.main()
