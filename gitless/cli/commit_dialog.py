# -*- coding: utf-8 -*-
# Gitless - a version control system built on top of Git.
# Licensed under GNU GPL v2.

"""Gitless's commit dialog."""


from __future__ import unicode_literals

import io
from locale import getpreferredencoding
import os
import subprocess
import sys
import shlex


from . import pprint


IS_PY2 = sys.version_info[0] == 2
ENCODING = getpreferredencoding() or 'utf-8'

_COMMIT_FILE = 'GL_COMMIT_EDIT_MSG'
_MERGE_MSG_FILE = 'MERGE_MSG'


def show(files, repo):
  """Show the commit dialog.

  Args:
    files: files for pre-populating the dialog.
    repo: the repository.

  Returns:
    The commit msg.
  """
  if IS_PY2:
    # wb because we use pprint to write
    cf = io.open(_commit_file(repo), mode='wb')
  else:
    cf = io.open(_commit_file(repo), mode='w', encoding=ENCODING)

  curr_b = repo.current_branch
  if curr_b.merge_in_progress or curr_b.fuse_in_progress:
    merge_msg = io.open(
        _merge_msg_file(repo), mode='r', encoding=ENCODING).read()
    cf.write(merge_msg)
  cf.write('\n')
  pprint.sep(stream=cf.write)
  pprint.msg(
      'Please enter the commit message for your changes above, an empty '
      'message aborts', stream=cf.write)
  pprint.msg('the commit.', stream=cf.write)
  pprint.blank(stream=cf.write)
  pprint.msg(
      'These are the files whose changes will be committed:', stream=cf.write)
  for f in files:
    pprint.item(f, stream=cf.write)
  pprint.sep(stream=cf.write)
  cf.close()
  _launch_editor(cf.name, repo)
  return _extract_msg(repo)


def _launch_editor(fp, repo):
  try:
    editor = repo.config['core.editor']
  except KeyError:
    editor = os.environ['EDITOR'] if 'EDITOR' in os.environ else 'vim'

  cmd = shlex.split(editor)
  cmd.append(fp)

  try:
    ret = subprocess.call(cmd)
    if ret != 0:
      pprint.err('Call to editor {0} failed'.format(editor))
  except OSError:
    pprint.err('Couldn\'t launch editor {0}'.format(editor))
    pprint.err_exp('change the value of git\'s core.editor setting')


def _extract_msg(repo):
  cf = io.open(_commit_file(repo), mode='r', encoding=ENCODING)
  sep = pprint.SEP + '\n'
  msg = ''
  l = cf.readline()
  while l != sep and len(l) > 0:
    msg += l
    l = cf.readline()
  # We reached the separator, this marks the end of the commit msg

  return msg


def _commit_file(repo):
  return os.path.join(repo.path, _COMMIT_FILE)


def _merge_msg_file(repo):
  return os.path.join(repo.path, _MERGE_MSG_FILE)
