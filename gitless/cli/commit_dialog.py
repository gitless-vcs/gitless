# Gitless - a version control system built on top of Git.
# Licensed under GNU GPL v2.

"""Gitless's commit dialog."""


import os
import subprocess

from gitless.core import repo as repo_lib

from . import pprint


_COMMIT_FILE = '.GL_COMMIT_EDIT_MSG'
_MERGE_MSG_FILE = 'MERGE_MSG'


def show(files, repo):
  """Show the commit dialog.

  Args:
    files: files for pre-populating the dialog.
    repo: the repository.

  Returns:
    The commit msg.
  """
  cf = open(_commit_file(repo), 'w')
  if repo.current_branch.merge_in_progress:
    merge_msg = open(_merge_msg_file(repo), 'r').read()
    cf.write(merge_msg)
  elif repo.current_branch.rebase_in_progress:
    pprint.msg(
        'The commit will have the original commit message', p=cf.write)
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
  for f in files:
    pprint.item(f, p=cf.write)
  pprint.sep(p=cf.write)
  cf.close()
  _launch_editor(cf.name)
  return _extract_msg(repo)


def _launch_editor(fp):
  editor = repo_lib.editor()
  if subprocess.call([editor, fp]) != 0:
    raise Exception('Call to editor {0} failed'.format(editor))


def _extract_msg(repo):
  cf = open(_commit_file(repo), 'r')
  sep = pprint.SEP + '\n'
  msg = ''
  l = cf.readline()
  while l != sep:
    msg += l
    l = cf.readline()
  # We reached the separator, this marks the end of the commit msg

  return msg


def _commit_file(repo):
  return os.path.join(repo.path, _COMMIT_FILE)


def _merge_msg_file(repo):
  return os.path.join(repo.path, _MERGE_MSG_FILE)
