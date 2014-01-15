# Gitless - a version control system built on top of Git.
# Copyright (c) 2013  Santiago Perez De Rosso.
# Licensed under GNU GPL, version 2.

"""Gitless's commit dialog."""


import os
import subprocess

from gitless.core import repo as repo_lib
from gitless.core import sync as sync_lib

import pprint


_COMMIT_FILE = '.GL_COMMIT_EDIT_MSG'
_MERGE_MSG_FILE = 'MERGE_MSG'  # TODO(sperezde): refactor this.


def show(files):
  """Show the dialog.

  Args:
    files: files for pre-populating the dialog.

  Returns:
    A tuple (msg, files) with the commit msg and the files to commit.
  """
  if sync_lib.merge_in_progress():
    return _show_merge(files)
  elif sync_lib.rebase_in_progress():
    return _show_rebase(files)
  return _show(files)


def _show(files):
  """Show the dialog.

  Args:
    files: files for pre-populating the dialog.

  Returns:
    A tuple (msg, files) with the commit msg and the files to commit.
  """
  # TODO(sperezde): detect if user exited with q!.
  cf = open(_commit_file(), 'w')
  cf.write('\n')
  pprint.sep(p=cf.write)
  pprint.msg(
      'Please enter the commit message for your changes above. Lines starting '
      'with', p=cf.write)
  pprint.msg(
      '\'#\' will be ignored, and an empty message aborts the commit.',
      p=cf.write)
  pprint.blank(p=cf.write)
  pprint.msg('These are the files that will be commited:', p=cf.write)
  pprint.exp('You can add/remove files to this list', p=cf.write)
  for f in files:
    pprint.item(f, p=cf.write)
  pprint.sep(p=cf.write)
  cf.close()
  _launch_editor()
  return _extract_info(5)


def _show_merge(files):
  """Show the dialog for a merge commit.

  Args:
    files: files that will be commited as part of the merge.

  Returns:
    A tuple (msg, files) with the commit msg and the files to commit.
  """
  cf = open(_commit_file(), 'w')
  merge_msg = open(_merge_msg_file(), 'r').read()
  cf.write(merge_msg)
  pprint.sep(p=cf.write)
  pprint.msg(
      'Please enter the commit message for your changes above. Lines starting '
      'with', p=cf.write)
  pprint.msg(
      '\'#\' will be ignored, and an empty message aborts the commit.',
      p=cf.write)
  pprint.blank(p=cf.write)
  pprint.msg(
      'These are the files that will be commited as part of the merge:',
      p=cf.write)
  pprint.exp(
      'You can add/remove files to this list, but you must commit resolved '
      'files', p=cf.write)
  for f in files:
    pprint.item(f, p=cf.write)
  pprint.sep(p=cf.write)
  cf.close()
  _launch_editor()
  return _extract_info(5)


def _show_rebase(files):
  """Show the dialog for a rebase commit.

  Args:
    files: files that will be commited as part of the rebase.

  Returns:
    A tuple (msg, files) with the commit msg and the files to commit.
  """
  # TODO(sperezde): let the user enter a message.
  cf = open(_commit_file(), 'w')
  #cf.write('\n')
  pprint.sep(p=cf.write)
  pprint.msg(
      'The commit will have the original commit message.', p=cf.write)
  pprint.blank(p=cf.write)
  pprint.msg(
      'These are the files that will be commited as part of the rebase:',
      p=cf.write)
  pprint.exp(
      'You can add/remove files to this list, but you must commit resolved '
      'files', p=cf.write)
  for f in files:
    pprint.item(f, p=cf.write)
  pprint.sep(p=cf.write)
  cf.close()
  _launch_editor()
  return _extract_info(4)


def _launch_editor():
  editor = repo_lib.editor()
  if subprocess.call('%s %s' % (editor, _commit_file()), shell=True) != 0:
    raise Exception('Call to editor %s failed' % editor)


def _extract_info(exp_lines):
  """Extracts the commit msg and files to commit from the commit file.

  Args:
    exp_lines: the amount of lines between the separator and when the actual
    file list begins.

  Returns:
    A tuple (msg, files) where msg is the commit msg and files are the files to
    commit provided by the user in the editor.
  """
  cf = open(_commit_file(), "r")
  sep = pprint.sep(lambda x: x)
  msg = ''
  l = cf.readline()
  while l != sep:
    msg += l
    l = cf.readline()
  # We reached the separator, this marks the end of the commit msg.
  # We exhaust the following lines so that we get to the file list.
  for i in range(0, exp_lines):
    cf.readline()

  files = []
  l = cf.readline()
  while l != sep:
    files.append(l[1:].strip())
    l = cf.readline()

  # We reached the separator, this marks the end of the file list.
  return msg, files


def _commit_file():
  return os.path.join(repo_lib.gl_dir(), _COMMIT_FILE)


def _merge_msg_file():
  return os.path.join(repo_lib.gl_dir(), _MERGE_MSG_FILE)
