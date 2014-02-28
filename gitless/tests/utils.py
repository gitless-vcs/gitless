# Gitless - a version control system built on top of Git.
# Licensed under GNU GPL, version 2.

"""Utility library for tests."""


import logging
import os
import shutil
import subprocess
import sys
import tempfile
import unittest


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

  # Python 2/3 compatibility.
  def assertItemsEqual(self, actual, expected, msg=None):
    try:
      return super(TestBase, self).assertItemsEqual(actual, expected, msg=msg)
    except AttributeError:
      try:
        return super(TestBase, self).assertCountEqual(actual, expected, msg=msg)
      except AttributeError:
        return self.assertEqual(sorted(actual), sorted(expected), msg=msg)


def write_file(fp, contents='hello'):
  dirs, _ = os.path.split(fp)
  if dirs and not os.path.exists(dirs):
    os.makedirs(dirs)
  f = open(fp, 'w')
  f.write(contents)
  f.close()


def append_to_file(fp, contents='hello'):
  f = open(fp, 'a')
  f.write(contents)
  f.close()


def read_file(fp):
  f = open(fp, 'r')
  ret = f.read()
  f.close()
  return ret


def gl_call(cmd, expected_ret_code=0, pre_cmd=None):
  return _call('gl', cmd, expected_ret_code=expected_ret_code, pre_cmd=pre_cmd)


def git_call(cmd, expected_ret_code=0):
  return _call('git', cmd, expected_ret_code=expected_ret_code)


def gl_expect_success(cmd, pre_cmd=None):
  return gl_call(cmd, pre_cmd=pre_cmd)


def gl_expect_error(cmd, pre_cmd=None):
  return gl_call(cmd, expected_ret_code=1, pre_cmd=pre_cmd)


def set_test_config():
  git_call('config user.name \"test\"')
  git_call('config user.email \"test@test.com\"')


# Private functions.


def _call(cmd, subcmd, expected_ret_code=0, pre_cmd=None):
  logging.debug('Calling {0} {1}'.format(cmd, subcmd))
  if pre_cmd:
    pre_cmd = pre_cmd + '|'
  else:
    pre_cmd = ''
  p = subprocess.Popen(
      '{0} {1} {2}'.format(pre_cmd, cmd, subcmd), stdout=subprocess.PIPE,
      stderr=subprocess.PIPE, shell=True)
  out, err = p.communicate()
  # Python 2/3 compatibility.
  if sys.version > "3":
    # Disable pylint's no-member error. 'str' has no 'decode' member in
    # python 3.
    # pylint: disable=E1101
    out = out.decode('utf-8')
    err = err.decode('utf-8')
  logging.debug('Out is \n{0}'.format(out))
  if err:
    logging.debug('Err is \n{0}'.format(err))
  if p.returncode != expected_ret_code:
    raise Exception(
        'Obtained ret code {0} doesn\'t match the expected {1}.\nOut of the'
        'cmd was:\n{2}\nErr of the cmd was:\n{3}\n'.format(
            p.returncode, expected_ret_code, out, err))
  return out, err
