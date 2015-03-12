# -*- coding: utf-8 -*-
# Gitless - a version control system built on top of Git.
# Licensed under GNU GPL, version 2.

"""Utility library for tests."""


import logging
import os
import shutil
import sys
import tempfile
import unittest

from sh import git


class TestBase(unittest.TestCase):

  def setUp(self, prefix_for_tmp_repo):
    """Creates temporary dir and cds to it."""
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    self.path = tempfile.mkdtemp(prefix=prefix_for_tmp_repo)
    logging.debug('Created temporary directory {0}'.format(self.path))
    os.chdir(self.path)

  def tearDown(self):
    """Removes the temporary dir."""
    shutil.rmtree(self.path)
    logging.debug('Removed dir {0}'.format(self.path))

  # Python 2/3 compatibility
  def assertItemsEqual(self, actual, expected, msg=None):
    try:
      return super(TestBase, self).assertItemsEqual(actual, expected, msg=msg)
    except AttributeError:
      try:
        return super(TestBase, self).assertCountEqual(actual, expected, msg=msg)
      except AttributeError:
        return self.assertEqual(sorted(actual), sorted(expected), msg=msg)


def write_file(fp, contents=None):
  _x_file('w', fp, contents=contents)


def append_to_file(fp, contents=None):
  _x_file('a', fp, contents=contents)


def read_file(fp):
  with open(fp, 'r') as f:
    ret = f.read()
  return ret


def set_test_config():
  git.config('user.name', 'test')
  git.config('user.email', 'test@test.com')


# Private functions


def _x_file(x, fp, contents=None):
  if not contents:
    contents = fp
  dirs, _ = os.path.split(fp)
  if dirs and not os.path.exists(dirs):
    os.makedirs(dirs)
  with open(fp, x) as f:
    f.write(contents)
