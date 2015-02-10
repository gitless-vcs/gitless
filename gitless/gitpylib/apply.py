# gitpylib - a Python library for Git.
# Licensed under GNU GPL v2.


from . import common


def on_index(patch_file):
  ok, _, _ = common.git_call('apply --cached {0}'.format(patch_file))
  return ok
