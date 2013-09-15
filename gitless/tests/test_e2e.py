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
import unittest


class TestEndToEnd(unittest.TestCase):

  def setUp(self):
    # Create temporary dir and cd to it.
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    self.path = tempfile.mkdtemp(prefix='gl-e2e-test')
    logging.debug('Created temporary directory %s', self.path)
    os.chdir(self.path)

  def tearDown(self):
    shutil.rmtree(self.path)
    logging.debug('Removed dir %s', self.path)

  def __gl_call(self, cmd, expected_ret_code=0):
    logging.debug('Calling gl {}'.format(cmd))
    p = subprocess.Popen(
        'gl {}'.format(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        shell=True)
    out, err = p.communicate()
    logging.debug('Out is \n{}'.format(out))
    if err:
      logging.debug('Err is \n{}'.format(err))
    if p.returncode != expected_ret_code:
      self.fail(
          'Obtained ret code {} doesn\'t match the expected {}'.format(
              p.returncode, expected_ret_code))
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

  def test_e2e(self):
    self.__success('init')
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
    out, unused_err = self.__success('branch')
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


if __name__ == '__main__':
  unittest.main()
