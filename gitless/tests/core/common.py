# Gitless - a version control system built on top of Git.
# Copyright (c) 2013  Santiago Perez De Rosso.
# Licensed under GNU GPL, version 2.

"""Common methods used in unit tests."""


import logging
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

import gitless.core.file as file_lib


class TestCore(unittest.TestCase):
  """Base class for core tests."""

  def setUp(self):
    """Creates temporary dir and cds to it."""
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    self.path = tempfile.mkdtemp(prefix='gl-core-test')
    logging.debug('Created temporary directory {}'.format(self.path))
    os.chdir(self.path)

  def tearDown(self):
    """Removes the temporary dir."""
    shutil.rmtree(self.path)
    logging.debug('Removed dir {}'.format(self.path))

  def _write_file(self, fp, contents='hello'):
    dirs, _ = os.path.split(fp)
    if dirs:
      os.makedirs(dirs)
    f = open(fp, 'w')
    f.write(contents)
    f.close()

  def _append_to_file(self, fp, contents='hello'):
    f = open(fp, 'a')
    f.write(contents)
    f.close()

  def _read_file(self, fp):
    f = open(fp, 'r')
    ret = f.read()
    f.close()
    return ret

  def _git_call(self, subcmd):
    """Issues a git call with the given subcmd.

    Args:
      subcmd: e.g., 'add f1'.
    """
    logging.debug('Calling git {}'.format(subcmd))
    p = subprocess.Popen(
        'git {}'.format(subcmd), stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, shell=True)
    out, err = p.communicate()
    if p.returncode != 0:
      raise Exception('Git call {} failed \nout:{} \nerr:{}'.format(
          subcmd, out, err))


def assert_contents_unchanged(fp):
  """Decorator that fails the test if the contents of the file fp changed.

  The method decorated should be a unit test.

  Usage:
    @common.assert_contents_unchanged('f1')
    def test_method_that_shouldnt_modify_f1(self):
      # do something here.
      # assert something here.

  Args:
    fp: the filepath to assert.
  """
  def decorator(f):
    def wrapper(*args, **kwargs):
      self = args[0]
      contents = self._read_file(fp)
      f(*args, **kwargs)
      contents_prime = self._read_file(fp)
      self.assertEqual(
          contents, contents_prime,
          'Contents of file changed: from {} to {}'.format(
              contents, contents_prime))
    return wrapper
  return decorator


def assert_status_unchanged(fp):
  """Decorator that fails the test if the status of fp changed.

  The method decorated should be a unit test.

  Usage:
    @common.assert_status_unchanged('f1')
    def test_method_that_shouldnt_modify_f1_status(self):
      # do something here.
      # assert something here.

  Args:
    fp: the filepath to assert.
  """
  def decorator(f):
    def wrapper(*args, **kwargs):
      self = args[0]
      s = file_lib.status(fp)
      f(*args, **kwargs)
      s_prime = file_lib.status(fp)
      self.assertEqual(
          s, s_prime,
          'Status of file changed: from {} to {}'.format(s, s_prime))
    return wrapper
  return decorator


def assert_no_side_effects(fp):
  """Decorator that fails the test if the contents or status of fp changed.

  The method decorated should be a unit test.

  Usage:
    @common.assert_no_side_effects('f1')
    def test_method_that_shouldnt_affect_f1(self):
      # do something here.
      # assert something here.

  It is a shorthand of:
    @common.assert_status_unchanged('f1')
    @common.assert_contents_unchanged('f1')
    def test_method_that_shouldnt_affect_f1(self):
      # do something here.
      # assert something here.

  Args:
    fp: the filepath to assert.
  """
  def decorator(f):
    @assert_contents_unchanged(fp)
    @assert_status_unchanged(fp)
    def wrapper(*args, **kwargs):
      f(*args, **kwargs)
    return wrapper
  return decorator
