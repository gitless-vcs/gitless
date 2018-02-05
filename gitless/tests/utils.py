# -*- coding: utf-8 -*-
# Gitless - a version control system built on top of Git
# Licensed under MIT

"""Utility library for tests."""


from __future__ import unicode_literals

import io
from locale import getpreferredencoding
import logging
import os
import re
import shutil
import stat
import sys
import tempfile
import unittest

if sys.platform != 'win32':
  from sh import git, ErrorReturnCode
else:
  from pbs import ErrorReturnCode, Command
  git = Command('git')


IS_PY2 = sys.version_info[0] == 2
ENCODING = getpreferredencoding() or 'utf-8'


class TestBase(unittest.TestCase):

  def setUp(self, prefix_for_tmp_repo):
    """Creates temporary dir and cds to it."""
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    self.path = tempfile.mkdtemp(prefix=prefix_for_tmp_repo)
    logging.debug('Created temporary directory {0}'.format(self.path))
    os.chdir(self.path)

  def tearDown(self):
    """Removes the temporary dir."""
    rmtree(self.path)

  # Python 2/3 compatibility
  def assertItemsEqual(self, actual, expected, msg=None):
    try:
      return super(TestBase, self).assertItemsEqual(actual, expected, msg=msg)
    except AttributeError:
      try:
        # Checks that actual and expected have the same elements in the same
        # number, regardless of their order
        return super(TestBase, self).assertCountEqual(actual, expected, msg=msg)
      except AttributeError:
        return self.assertEqual(sorted(actual), sorted(expected), msg=msg)

  def assertRaisesRegexp(self, exc, r, fun, *args, **kwargs):
    try:
      fun(*args, **kwargs)
      self.fail('Exception not raised')
    except exc as e:
      msg = stderr(e) if isinstance(e, ErrorReturnCode) else str(e)
      if not re.search(r, msg):
        self.fail('No "{0}" found in "{1}"'.format(r, msg))


def rmtree(path):
  # On Windows, running shutil.rmtree on a folder that contains read-only
  # files throws errors. To workaround this, if removing a path fails, we make
  # the path writable and then try again
  def onerror(func, path, unused_exc_info):  # error handler for rmtree
    if not os.access(path, os.W_OK):
      os.chmod(path, stat.S_IWUSR)
      func(path)
    else:
      # Swallow errors for now (on Windows there seems to be something weird
      # going on and we can't remove the temp directory even after all files
      # in it have been successfully removed)
      pass

  shutil.rmtree(path, onerror=onerror)
  logging.debug('Removed dir {0}'.format(path))


def write_file(fp, contents=''):
  _x_file('w', fp, contents=contents)


def append_to_file(fp, contents=''):
  _x_file('a', fp, contents=contents)


def set_test_config():
  git.config('user.name', 'test')
  git.config('user.email', 'test@test.com')


def read_file(fp):
  with io.open(fp, mode='r', encoding=ENCODING) as f:
    ret = f.read()
  return ret


def stdout(p):
  return p.stdout.decode(ENCODING)


def stderr(p):
  return p.stderr.decode(ENCODING)


# Private functions


def _x_file(x, fp, contents=''):
  assert not IS_PY2 or isinstance(contents, unicode)

  if not contents:
    contents = fp
  dirs, _ = os.path.split(fp)
  if dirs and not os.path.exists(dirs):
    os.makedirs(dirs)
  with io.open(fp, mode=x, encoding=ENCODING) as f:
    f.write(contents)
