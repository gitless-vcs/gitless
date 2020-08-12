# -*- coding: utf-8 -*-
# Gitless - a version control system built on top of Git
# Licensed under MIT

"""End-to-end test."""


import logging
import os
import re
import time
from subprocess import CalledProcessError
import sys

from gitless.tests import utils

try:
  text = unicode
except NameError:
  text = str


class TestEndToEnd(utils.TestBase):

  def setUp(self):
    super(TestEndToEnd, self).setUp('gl-e2e-test')
    utils.gl('init')
    # Disable colored output so that we don't need to worry about ANSI escape
    # codes
    utils.git('config', 'color.ui', 'False')
    # Disable paging so that we don't have to use sh's _tty_out option, which is
    # not available on pbs
    if sys.platform != 'win32':
      utils.git('config', 'core.pager', 'cat')
    else:
      # On Windows, we need to call 'type' through cmd.exe (with 'cmd'). The /C
      # is so that the command window gets closed after 'type' finishes
      utils.git('config', 'core.pager', 'cmd /C type')
    utils.set_test_config()


class TestNotInRepo(utils.TestBase):

  def setUp(self):
    super(TestNotInRepo, self).setUp('gl-e2e-test')

  def test_not_in_repo(self):
    def assert_not_in_repo(*cmds):
      for cmd in cmds:
        self.assertRaisesRegexp(
            CalledProcessError, 'not in a Gitless\'s repository', utils.gl, cmd)

    assert_not_in_repo(
      'status', 'diff', 'commit', 'branch', 'merge', 'fuse', 'remote',
      'publish', 'history')


class TestBasic(TestEndToEnd):

  def test_basic_functionality(self):
    utils.write_file('file1', 'Contents of file1')
    # Track
    utils.gl('track', 'file1')
    self.assertRaises(CalledProcessError, utils.gl, 'track', 'file1')
    self.assertRaises(CalledProcessError, utils.gl, 'track', 'non-existent')
    # Untrack
    utils.gl('untrack', 'file1')
    self.assertRaises(CalledProcessError, utils.gl, 'untrack', 'file1')
    self.assertRaises(CalledProcessError, utils.gl, 'untrack', 'non-existent')
    # Commit
    utils.gl('track', 'file1')
    utils.gl('commit', '-m', 'file1 commit')
    self.assertRaises(
      CalledProcessError, utils.gl, 'commit', '-m', 'nothing to commit')
    # History
    if 'file1 commit' not in utils.gl('history'):
      self.fail('Commit didn\'t appear in history')
    # Branch
    # Make some changes to file1 and branch out
    utils.write_file('file1', 'New contents of file1')
    utils.gl('branch', '-c', 'branch1')
    utils.gl('switch', 'branch1')
    if 'New' in utils.read_file('file1'):
      self.fail('Branch not independent!')
    # Switch back to master branch, check that contents are the same as before.
    utils.gl('switch', 'master')
    if 'New' not in utils.read_file('file1'):
      self.fail('Branch not independent!')
    out = utils.gl('branch')
    if '* master' not in out:
      self.fail('Branch status output wrong: {0}'.format(out))
    if 'branch1' not in out:
      self.fail('Branch status output wrong: {0}'.format(out))

    utils.gl('branch', '-c', 'branch2')
    utils.gl('branch', '-c', 'branch-conflict1')
    utils.gl('branch', '-c', 'branch-conflict2')
    utils.gl('commit', '-m', 'New contents commit')

    # Fuse
    utils.gl('switch', 'branch1')
    self.assertRaises(CalledProcessError, utils.gl, 'fuse')  # no upstream set
    try:
      utils.gl('fuse', 'master')
    except CalledProcessError as e:
      self.fail(utils.stderr(e))
    out = utils.gl('history')
    if 'file1 commit' not in out:
      self.fail(out)

    # Merge
    utils.gl('switch', 'branch2')
    self.assertRaises(CalledProcessError, utils.gl, 'merge')  # no upstream set
    utils.gl('merge', 'master')
    out = utils.gl('history')
    if 'file1 commit' not in out:
      self.fail(out)

    # Conflicting fuse
    utils.gl('switch', 'branch-conflict1')
    utils.write_file('file1', 'Conflicting changes to file1')
    utils.gl('commit', '-m', 'changes in branch-conflict1')
    try:
      utils.gl('fuse', 'master')
    except CalledProcessError as e:
      # expected
      err = e.stderr
      if 'conflict' not in err:
        self.fail(err)

    out = utils.gl('status')
    if 'file1 (with conflicts)' not in out:
      self.fail(out)

    # Try aborting
    utils.gl('fuse', '--abort')
    out = utils.gl('status')
    if 'file1' in out:
      self.fail(out)

    # Ok, now let's fix the conflicts
    try:
      utils.gl('fuse', 'master')
    except CalledProcessError as e:
      # expected
      err = e.stderr
      if 'conflict' not in err:
        self.fail(err)

    out = utils.gl('status')
    if 'file1 (with conflicts)' not in out:
      self.fail(out)

    utils.write_file('file1', 'Fixed conflicts!')
    self.assertRaises(
      CalledProcessError, utils.gl, 'commit', '-m', 'resolve not called')
    self.assertRaises(
      CalledProcessError, utils.gl, 'resolve', 'non-existent')
    utils.gl('resolve', 'file1')
    utils.gl('commit', '-m', 'fixed conflicts')


class TestCommit(TestEndToEnd):

  TRACKED_FP = 'file1'
  DIR_TRACKED_FP = 'dir/dir_file'
  UNTRACKED_FP = 'file2'
  FPS = [TRACKED_FP, DIR_TRACKED_FP, UNTRACKED_FP]
  DIR = 'dir'

  def setUp(self):
    super(TestCommit, self).setUp()
    utils.write_file(self.TRACKED_FP)
    utils.write_file(self.DIR_TRACKED_FP)
    utils.write_file(self.UNTRACKED_FP)
    utils.gl('track', self.TRACKED_FP, self.DIR_TRACKED_FP)

  def test_commit(self):
    utils.gl('commit', '-m', 'msg')
    self.__assert_commit(self.TRACKED_FP, self.DIR_TRACKED_FP)

  def test_commit_relative(self):
    os.chdir(self.DIR)
    utils.gl('commit', '-m', 'msg')
    self.__assert_commit(self.TRACKED_FP, self.DIR_TRACKED_FP)

  def test_commit_only(self):
    utils.gl('commit', self.TRACKED_FP, '-m', 'msg')
    self.__assert_commit(self.TRACKED_FP)

  def test_commit_only_relative(self):
    os.chdir(self.DIR)
    self.assertRaises(
      CalledProcessError, utils.gl, 'commit', self.TRACKED_FP, '-m', 'msg')
    utils.gl('commit', '../' + self.TRACKED_FP, '-m', 'msg')
    self.__assert_commit(self.TRACKED_FP)

  def test_commit_only_untrack(self):
    utils.gl('commit', '-m', 'msg', self.UNTRACKED_FP)
    self.__assert_commit(self.UNTRACKED_FP)

  def test_commit_only_untrack_relative(self):
    os.chdir(self.DIR)
    self.assertRaises(
      CalledProcessError, utils.gl, 'commit', self.UNTRACKED_FP, '-m', 'msg')
    utils.gl('commit', '../' + self.UNTRACKED_FP, '-m', 'msg')
    self.__assert_commit(self.UNTRACKED_FP)

  def test_commit_include(self):
    utils.gl('commit', '-m', 'msg', '--include', self.UNTRACKED_FP)
    self.__assert_commit(
        self.TRACKED_FP, self.DIR_TRACKED_FP, self.UNTRACKED_FP)

  def test_commit_exclude_include(self):
    utils.gl(
      'commit', '-m', 'msg',
      '--include', self.UNTRACKED_FP, '--exclude', self.TRACKED_FP)
    self.__assert_commit(self.UNTRACKED_FP, self.DIR_TRACKED_FP)

  def test_commit_no_files(self):
    self.assertRaises(
      CalledProcessError, utils.gl, 'commit', '--exclude',
      self.TRACKED_FP, self.DIR_TRACKED_FP, '-m', 'msg')
    self.assertRaises(
      CalledProcessError, utils.gl, 'commit', 'non-existent', '-m', 'msg')
    self.assertRaises(
      CalledProcessError, utils.gl, 'commit', '-m', 'msg',
      '--exclude', 'non-existent')
    self.assertRaises(
      CalledProcessError, utils.gl, 'commit', '-m', 'msg',
      '--include', 'non-existent')

  def test_commit_dir(self):
    fp = 'dir/f'
    utils.write_file(fp)
    utils.gl('commit', fp, '-m', 'msg')
    self.__assert_commit('dir/f')

  def __assert_commit(self, *expected_committed):
    h = utils.gl('history', '-v')
    for fp in expected_committed:
      if fp not in h:
        self.fail('{0} was apparently not committed!'.format(fp))
    expected_not_committed = [
        fp for fp in self.FPS if fp not in expected_committed]
    for fp in expected_not_committed:
      if fp in h:
        self.fail('{0} was apparently committed!'.format(fp))


class TestStatus(TestEndToEnd):

  DIR = 'dir'
  TRACKED_DIR_FP = os.path.join('dir', 'file1')
  UNTRACKED_DIR_FP = os.path.join('dir', 'file2')

  def setUp(self):
    super(TestStatus, self).setUp()
    utils.write_file(self.TRACKED_DIR_FP)
    utils.write_file(self.UNTRACKED_DIR_FP)
    utils.gl('commit', self.TRACKED_DIR_FP, '-m', 'commit')

  def test_status_relative(self):
    utils.write_file(self.TRACKED_DIR_FP, contents='some modifications')
    st = utils.gl('status')
    if self.TRACKED_DIR_FP not in st:
      self.fail()
    if self.UNTRACKED_DIR_FP not in st:
      self.fail()

    os.chdir(self.DIR)

    st = utils.gl('status')
    rel_tracked = os.path.relpath(self.TRACKED_DIR_FP, self.DIR)
    rel_untracked = os.path.relpath(self.UNTRACKED_DIR_FP, self.DIR)
    if (self.TRACKED_DIR_FP in st) or (rel_tracked not in st):
      self.fail()
    if (self.UNTRACKED_DIR_FP in st) or (rel_untracked not in st):
      self.fail()


class TestBranch(TestEndToEnd):

  BRANCH_1 = 'branch1'
  BRANCH_2 = 'branch2'

  def setUp(self):
    super(TestBranch, self).setUp()
    utils.write_file('f')
    utils.gl('commit', 'f', '-m', 'commit')

  def test_create(self):
    utils.gl('branch', '-c', self.BRANCH_1)
    self.assertRaises(
      CalledProcessError, utils.gl, 'branch', '-c', self.BRANCH_1)
    self.assertRaises(
      CalledProcessError, utils.gl, 'branch', '-c', 'evil*named*branch')
    if self.BRANCH_1 not in utils.gl('branch'):
      self.fail()

  def test_remove(self):
    utils.gl('branch', '-c', self.BRANCH_1)
    utils.gl('switch', self.BRANCH_1)
    self.assertRaises(
      CalledProcessError, utils.gl, 'branch', '-d', self.BRANCH_1, _in='y')
    utils.gl('branch', '-c', self.BRANCH_2)
    utils.gl('switch', self.BRANCH_2)
    utils.gl('branch', '-d', self.BRANCH_1, _in='n')
    utils.gl('branch', '-d', self.BRANCH_1, _in='y')
    if self.BRANCH_1 in utils.gl('branch'):
      self.fail()

  def test_upstream(self):
    self.assertRaises(CalledProcessError, utils.gl, 'branch', '-uu')
    self.assertRaises(
      CalledProcessError, utils.gl, 'branch', '-su', 'non-existent')
    self.assertRaises(
      CalledProcessError, utils.gl, 'branch', '-su', 'non-existent/non-existent')

  def test_list(self):
    utils.gl('branch', '-c', self.BRANCH_1)
    utils.gl('branch', '-c', self.BRANCH_2)
    branch_out = utils.gl('branch')
    self.assertTrue(
        branch_out.find(self.BRANCH_1) < branch_out.find(self.BRANCH_2))


class TestTag(TestEndToEnd):

  TAG_1 = 'tag1'
  TAG_2 = 'tag2'

  def setUp(self):
    super(TestTag, self).setUp()
    utils.write_file('f')
    utils.gl('commit', 'f', '-m', 'commit')

  def test_create(self):
    utils.gl('tag', '-c', self.TAG_1)
    self.assertRaises(CalledProcessError, utils.gl, 'tag', '-c', self.TAG_1)
    self.assertRaises(
      CalledProcessError, utils.gl, 'tag', '-c', 'evil*named*tag')
    if self.TAG_1 not in utils.gl('tag'):
      self.fail()

  def test_remove(self):
    utils.gl('tag', '-c', self.TAG_1)
    utils.gl('tag', '-d', self.TAG_1, _in='n')
    utils.gl('tag', '-d', self.TAG_1, _in='y')
    if self.TAG_1 in utils.gl('tag'):
      self.fail()

  def test_list(self):
    utils.gl('tag', '-c', self.TAG_1)
    utils.gl('tag', '-c', self.TAG_2)
    tag_out = utils.gl('tag')
    self.assertTrue(
        tag_out.find(self.TAG_1) < tag_out.find(self.TAG_2))


class TestDiffFile(TestEndToEnd):

  TRACKED_FP = 't_fp'
  DIR_TRACKED_FP = os.path.join('dir', 't_fp')
  UNTRACKED_FP = 'u_fp'
  DIR = 'dir'

  def setUp(self):
    super(TestDiffFile, self).setUp()
    utils.write_file(self.TRACKED_FP)
    utils.write_file(self.DIR_TRACKED_FP)
    utils.gl('commit', self.TRACKED_FP, self.DIR_TRACKED_FP, '-m', 'commit')
    utils.write_file(self.UNTRACKED_FP)

  def test_empty_diff(self):
    if 'No files to diff' not in utils.gl('diff'):
      self.fail()

  def test_diff_nonexistent_fp(self):
    try:
      utils.gl('diff', 'file')
    except CalledProcessError as e:
      # expected
      err = e.stderr
      if 'doesn\'t exist' not in err:
        self.fail()

  def test_basic_diff(self):
    utils.write_file(self.TRACKED_FP, contents='contents')
    out1 = utils.gl('diff')
    if '+contents' not in out1:
      self.fail()
    out2 = utils.gl('diff', self.TRACKED_FP)
    if '+contents' not in out2:
      self.fail()
    self.assertEqual(out1, out2)

  def test_basic_diff_relative(self):
    utils.write_file(self.TRACKED_FP, contents='contents_tracked')
    utils.write_file(self.DIR_TRACKED_FP, contents='contents_dir_tracked')
    os.chdir(self.DIR)
    out1 = utils.gl('diff')
    if '+contents_tracked' not in out1:
      self.fail()
    if '+contents_dir_tracked' not in out1:
      self.fail()
    rel_dir_tracked_fp = os.path.relpath(self.DIR_TRACKED_FP, self.DIR)
    out2 = utils.gl('diff', rel_dir_tracked_fp)
    if '+contents_dir_tracked' not in out2:
      self.fail()

  def test_diff_dir(self):
    fp = 'dir/dir/f'
    utils.write_file(fp, contents='contents')
    out = utils.gl('diff', fp)
    if '+contents' not in out:
      self.fail()

  def test_diff_non_ascii(self):
    if sys.platform == 'win32':
      # Skip this test on Windows until we fix Unicode support
      return
    contents = '’◕‿◕’©Ä☺’ಠ_ಠ’'
    utils.write_file(self.TRACKED_FP, contents=contents)
    out1 = utils.gl('diff')
    if '+' + contents not in out1:
      self.fail('out is ' + out1)
    out2 = utils.gl('diff', self.TRACKED_FP)
    if '+' + contents not in out2:
      self.fail('out is ' + out2)
    self.assertEqual(out1, out2)


class TestOp(TestEndToEnd):

  COMMITS_NUMBER = 4
  OTHER = 'other'
  MASTER_FILE = 'master_file'
  OTHER_FILE = 'other_file'

  def setUp(self):
    super(TestOp, self).setUp()

    self.commits = {}
    def create_commits(branch_name, fp):
      self.commits[branch_name] = []
      utils.append_to_file(fp, contents='contents {0}\n'.format(0))
      out = utils.gl(
        'commit', '-m', 'ci 0 in {0}'.format(branch_name), '--include', fp)
      self.commits[branch_name].append(
          re.search(r'Commit Id: (\S*)', out, re.UNICODE).group(1))
      for i in range(1, self.COMMITS_NUMBER):
        utils.append_to_file(fp, contents='contents {0}\n'.format(i))
        out = utils.gl('commit', '-m', 'ci {0} in {1}'.format(i, branch_name))
        self.commits[branch_name].append(
            re.search(r'Commit Id: (\S*)', out, re.UNICODE).group(1))

    utils.gl('branch', '-c', self.OTHER)
    create_commits('master', self.MASTER_FILE)
    try:
      utils.gl('switch', self.OTHER)
    except CalledProcessError as e:
      raise Exception(e.stderr)
    create_commits(self.OTHER, self.OTHER_FILE)
    utils.gl('switch', 'master')


class TestFuse(TestOp):

  def __assert_history(self, expected):
    out = utils.gl('history')
    cids = list(reversed(re.findall(r'ci (.*) in (\S*)', out, re.UNICODE)))
    self.assertCountEqual(
        cids, expected, 'cids is ' + text(cids) + ' exp ' + text(expected))

    st_out = utils.gl('status')
    self.assertFalse('fuse' in st_out)

  def __build(self, branch_name, cids=None):
    if not cids:
      cids = range(self.COMMITS_NUMBER)
    return [(text(ci), branch_name) for ci in cids]

  def test_basic(self):
    utils.gl('fuse', self.OTHER)
    self.__assert_history(self.__build(self.OTHER) + self.__build('master'))

  def test_only_errors(self):
    self.assertRaises(
      CalledProcessError, utils.gl, 'fuse', self.OTHER, '-o', 'non-existent-id')
    self.assertRaises(
      CalledProcessError, utils.gl, 'fuse', self.OTHER,
      '-o', self.commits['master'][1])

  def test_only_one(self):
    utils.gl('fuse', self.OTHER, '-o', self.commits[self.OTHER][0])
    self.__assert_history(
        self.__build(self.OTHER, cids=[0]) + self.__build('master'))

  def test_only_some(self):
    utils.gl('fuse', self.OTHER, '-o', *self.commits[self.OTHER][:2])
    self.__assert_history(
        self.__build(self.OTHER, [0, 1]) + self.__build('master'))

  def test_exclude_errors(self):
    self.assertRaises(
      CalledProcessError, utils.gl, 'fuse', self.OTHER, '-e', 'non-existent-id')
    self.assertRaises(
      CalledProcessError, utils.gl, 'fuse', self.OTHER,
      '-e', self.commits['master'][1])

  def test_exclude_one(self):
    last_ci = self.COMMITS_NUMBER - 1
    utils.gl('fuse', self.OTHER, '-e', self.commits[self.OTHER][last_ci])
    self.__assert_history(
        self.__build(self.OTHER, range(0, last_ci)) + self.__build('master'))

  def test_exclude_some(self):
    utils.gl('fuse', self.OTHER, '-e', *self.commits[self.OTHER][1:])
    self.__assert_history(
        self.__build(self.OTHER, cids=[0]) + self.__build('master'))

  def test_ip_dp(self):
    utils.gl('fuse', self.OTHER, '--insertion-point', 'dp')
    self.__assert_history(self.__build(self.OTHER) + self.__build('master'))

  def test_ip_head(self):
    utils.gl('fuse', self.OTHER, '--insertion-point', 'HEAD')
    self.__assert_history(self.__build('master') + self.__build(self.OTHER))

  def test_ip_commit(self):
    utils.gl('fuse', self.OTHER, '--insertion-point', self.commits['master'][1])
    self.__assert_history(
        self.__build('master', [0, 1]) + self.__build(self.OTHER) +
        self.__build('master', range(2, self.COMMITS_NUMBER)))

  def test_conflicts(self):
    def trigger_conflicts():
      self.assertRaisesRegexp(
          CalledProcessError, 'conflicts', utils.gl, 'fuse',
          self.OTHER, '-e', self.commits[self.OTHER][0])

    # Abort
    trigger_conflicts()
    utils.gl('fuse', '-a')
    self.__assert_history(self.__build('master'))

    # Fix conflicts
    trigger_conflicts()
    utils.gl('resolve', self.OTHER_FILE)
    utils.gl('commit', '-m', 'ci 1 in other')
    self.__assert_history(
        self.__build(self.OTHER, range(1, self.COMMITS_NUMBER)) +
        self.__build('master'))

  def test_conflicts_switch(self):
    utils.gl('switch', 'other')
    utils.write_file(self.OTHER_FILE, contents='uncommitted')
    utils.gl('switch', 'master')
    try:
      utils.gl('fuse', self.OTHER, '-e', self.commits[self.OTHER][0])
      self.fail()
    except CalledProcessError:
      pass

    # Switch
    utils.gl('switch', 'other')
    self.__assert_history(self.__build('other'))
    st_out = utils.gl('status')
    self.assertTrue('fuse' not in st_out)
    self.assertTrue('conflict' not in st_out)

    utils.gl('switch', 'master')
    st_out = utils.gl('status')
    self.assertTrue('fuse' in st_out)
    self.assertTrue('conflict' in st_out)

    # Check that we are able to complete the fuse after switch
    utils.gl('resolve', self.OTHER_FILE)
    utils.gl('commit', '-m', 'ci 1 in other')
    self.__assert_history(
        self.__build(self.OTHER, range(1, self.COMMITS_NUMBER)) +
        self.__build('master'))

    utils.gl('switch', 'other')
    self.assertEqual('uncommitted', utils.read_file(self.OTHER_FILE))

  def test_conflicts_multiple(self):
    utils.gl('branch', '-c', 'tmp', '--divergent-point', 'HEAD~2')
    utils.gl('switch', 'tmp')
    utils.append_to_file(self.MASTER_FILE, contents='conflict')
    utils.gl('commit', '-m', 'will conflict 0')
    utils.append_to_file(self.MASTER_FILE, contents='conflict')
    utils.gl('commit', '-m', 'will conflict 1')

    self.assertRaisesRegexp(
      CalledProcessError, 'conflicts', utils.gl, 'fuse', 'master')
    utils.gl('resolve', self.MASTER_FILE)
    self.assertRaisesRegexp(
      CalledProcessError, 'conflicts', utils.gl, 'commit', '-m', 'ci 0 in tmp')
    utils.gl('resolve', self.MASTER_FILE)
    utils.gl('commit', '-m', 'ci 1 in tmp')  # this one should finalize the fuse

    self.__assert_history(
        self.__build('master') + self.__build('tmp', range(2)))

  def test_conflicts_multiple_uncommitted_changes(self):
    utils.gl('branch', '-c', 'tmp', '--divergent-point', 'HEAD~2')
    utils.gl('switch', 'tmp')
    utils.append_to_file(self.MASTER_FILE, contents='conflict')
    utils.gl('commit', '-m', 'will conflict 0')
    utils.append_to_file(self.MASTER_FILE, contents='conflict')
    utils.gl('commit', '-m', 'will conflict 1')
    utils.write_file(self.MASTER_FILE, contents='uncommitted')

    self.assertRaisesRegexp(
      CalledProcessError, 'conflicts', utils.gl, 'fuse', 'master')
    utils.gl('resolve', self.MASTER_FILE)
    self.assertRaisesRegexp(
      CalledProcessError, 'conflicts', utils.gl, 'commit', '-m', 'ci 0 in tmp')
    utils.gl('resolve', self.MASTER_FILE)
    self.assertRaisesRegexp(
      CalledProcessError, 'failed to apply', utils.gl,
      'commit', '-m', 'ci 1 in tmp')

    self.__assert_history(
        self.__build('master') + self.__build('tmp', range(2)))
    self.assertTrue('Stashed' in utils.read_file(self.MASTER_FILE))

  def test_nothing_to_fuse(self):
    self.assertRaisesRegexp(
      CalledProcessError, 'No commits to fuse', utils.gl, 'fuse',
      self.OTHER, '-e', *self.commits[self.OTHER])

  def test_ff(self):
    utils.gl('branch', '-c', 'tmp', '--divergent-point', 'HEAD~2')
    utils.gl('switch', 'tmp')

    utils.gl('fuse', 'master')
    self.__assert_history(self.__build('master'))

  def test_ff_ip_head(self):
    utils.gl('branch', '-c', 'tmp', '--divergent-point', 'HEAD~2')
    utils.gl('switch', 'tmp')

    utils.gl('fuse', 'master', '--insertion-point', 'HEAD')
    self.__assert_history(self.__build('master'))

  def test_uncommitted_changes(self):
    utils.write_file(self.MASTER_FILE, contents='uncommitted')
    utils.write_file('master_untracked', contents='uncommitted')
    utils.gl('fuse', self.OTHER)
    self.assertEqual('uncommitted', utils.read_file(self.MASTER_FILE))
    self.assertEqual('uncommitted', utils.read_file('master_untracked'))

  def test_uncommitted_tracked_changes_that_conflict(self):
    utils.gl('branch', '-c', 'tmp', '--divergent-point', 'HEAD~1')
    utils.gl('switch', 'tmp')
    utils.write_file(self.MASTER_FILE, contents='uncommitted')
    self.assertRaisesRegexp(
      CalledProcessError, 'failed to apply', utils.gl, 'fuse',
      'master', '--insertion-point', 'HEAD')
    contents = utils.read_file(self.MASTER_FILE)
    self.assertTrue('uncommitted' in contents)
    self.assertTrue('contents 2' in contents)

  def test_uncommitted_tracked_changes_that_conflict_append(self):
    utils.gl('branch', '-c', 'tmp', '--divergent-point', 'HEAD~1')
    utils.gl('switch', 'tmp')
    utils.append_to_file(self.MASTER_FILE, contents='uncommitted')
    self.assertRaisesRegexp(
        CalledProcessError, 'failed to apply', utils.gl, 'fuse',
        'master', '--insertion-point', 'HEAD')
    contents = utils.read_file(self.MASTER_FILE)
    self.assertTrue('uncommitted' in contents)
    self.assertTrue('contents 2' in contents)

#  def test_uncommitted_untracked_changes_that_conflict(self):
#    utils.write_file(self.OTHER_FILE, contents='uncommitted in master')
#    try:
#      utils.gl('fuse', self.OTHER)
#      self.fail()
#    except CalledProcessError as e:
#      self.assertTrue('failed to apply' in utils.stderr(e))


class TestMerge(TestOp):

  def test_uncommitted_changes(self):
    utils.write_file(self.MASTER_FILE, contents='uncommitted')
    utils.write_file('master_untracked', contents='uncommitted')
    utils.gl('merge', self.OTHER)
    self.assertEqual('uncommitted', utils.read_file(self.MASTER_FILE))
    self.assertEqual('uncommitted', utils.read_file('master_untracked'))

  def test_uncommitted_tracked_changes_that_conflict(self):
    utils.gl('branch', '-c', 'tmp', '--divergent-point', 'HEAD~1')
    utils.gl('switch', 'tmp')
    utils.write_file(self.MASTER_FILE, contents='uncommitted')
    self.assertRaisesRegexp(
        CalledProcessError, 'failed to apply', utils.gl, 'merge', 'master')
    contents = utils.read_file(self.MASTER_FILE)
    self.assertTrue('uncommitted' in contents)
    self.assertTrue('contents 2' in contents)

  def test_uncommitted_tracked_changes_that_conflict_append(self):
    utils.gl('branch', '-c', 'tmp', '--divergent-point', 'HEAD~1')
    utils.gl('switch', 'tmp')
    utils.append_to_file(self.MASTER_FILE, contents='uncommitted')
    self.assertRaisesRegexp(
      CalledProcessError, 'failed to apply', utils.gl, 'merge', 'master')
    contents = utils.read_file(self.MASTER_FILE)
    self.assertTrue('uncommitted' in contents)
    self.assertTrue('contents 2' in contents)


class TestPerformance(TestEndToEnd):

  FPS_QTY = 10000

  def setUp(self):
    super(TestPerformance, self).setUp()
    for i in range(0, self.FPS_QTY):
      fp = 'f' + text(i)
      utils.write_file(fp, fp)

  def test_status_performance(self):
    def assert_status_performance():
      # The test fails if `gl status` takes more than 100 times
      # the time `git status` took.
      MAX_TOLERANCE = 100

      t = time.time()
      utils.gl('status')
      gl_t = time.time() - t

      t = time.time()
      utils.git('status')
      git_t = time.time() - t

      self.assertTrue(
          gl_t < git_t*MAX_TOLERANCE,
          msg='gl_t {0}, git_t {1}'.format(gl_t, git_t))

    # All files are untracked
    assert_status_performance()
    # Track all files, repeat
    logging.info('Doing a massive git add, this might take a while')
    utils.git('add', '.')
    logging.info('Done')
    assert_status_performance()

  def test_branch_switch_performance(self):
    MAX_TOLERANCE = 100

    utils.gl('commit', 'f1', '-m', 'commit')

    t = time.time()
    utils.gl('branch', '-c', 'develop')
    utils.gl('switch', 'develop')
    gl_t = time.time() - t

    # go back to previous state
    utils.gl('switch', 'master')

    # do the same for git
    t = time.time()
    utils.git('branch', 'gitdev')
    utils.git('stash', 'save', '--all')
    utils.git('checkout', 'gitdev')
    git_t = time.time() - t

    self.assertTrue(
        gl_t < git_t*MAX_TOLERANCE,
        msg='gl_t {0}, git_t {1}'.format(gl_t, git_t))
