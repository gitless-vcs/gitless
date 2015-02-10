# gitpylib - a Python library for Git.
# Licensed under GNU GPL v2.

"""Hook module for running Git hooks."""


import collections
import os
import subprocess

from . import common


def pre_commit():
  """Runs the pre-commit hook."""
  return _hook_call('pre-commit')


def _hook_call(hook_name):
  HookCall = collections.namedtuple('hook_call', ['ok', 'out', 'err'])
  hook_path = '{0}/hooks/{1}'.format(common.git_dir(), hook_name)
  if not os.path.exists(hook_path):
    return HookCall(True, '', '')
  p = subprocess.Popen(
      hook_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
  out, err = p.communicate()
  return HookCall(p.returncode == 0, out, err)
