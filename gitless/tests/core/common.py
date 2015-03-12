# Gitless - a version control system built on top of Git.
# Licensed under GNU GPL v2.

"""Common methods used in unit tests."""


from functools import wraps
import os

from gitless import core
import gitless.tests.utils as utils_lib


class TestCore(utils_lib.TestBase):
  """Base class for core tests."""

  def setUp(self):
    super(TestCore, self).setUp('gl-core-test')
    utils_lib.git_call('init')
    utils_lib.set_test_config()
    self.repo = core.Repository()


def assert_contents_unchanged(*fps):
  """Decorator that fails the test if the contents of the file fp changed.

  The method decorated should be a unit test.

  Usage:
    @common.assert_contents_unchanged('f1')
    def test_method_that_shouldnt_modify_f1(self):
      # do something here.
      # assert something here.

  Args:
    fps: the filepath(s) to assert.
  """
  def prop(*args, **kwargs):
    return utils_lib.read_file
  return __assert_decorator('Contents', prop, *fps)


def assert_status_unchanged(*fps):
  """Decorator that fails the test if the status of fp changed.

  The method decorated should be a unit test.

  Usage:
    @common.assert_status_unchanged('f1')
    def test_method_that_shouldnt_modify_f1_status(self):
      # do something here.
      # assert something here.

  Args:
    fps: the filepath(s) to assert.
  """
  def prop(self, *args, **kwargs):
    return self.curr_b.status_file
  return __assert_decorator('Status', prop, *fps)


def assert_no_side_effects(*fps):
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
    fps: the filepath(s) to assert.
  """
  def decorator(f):
    @assert_contents_unchanged(*fps)
    @assert_status_unchanged(*fps)
    @wraps(f)
    def wrapper(*args, **kwargs):
      f(*args, **kwargs)
    return wrapper
  return decorator


# Private functions.


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
