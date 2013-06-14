"""Gitless's commit dialog."""


import os
import subprocess

import lib
import pprint


_COMMIT_FILE = '.GL_COMMIT_EDIT_MSG'


def show(files):
  """Show the dialog.

  Args:
    files: files for pre-populating the dialog.

  Returns:
    A tuple (msg, files) with the commit msg and the files to commit.
  """
  # TODO(sperezde): use git editor if present.
  # TODO(sperezde): detect if user exited with q!.
  cf = open(_commit_file(), 'w')
  cf.write('\n')
  pprint.sep(cf.write)
  pprint.msg(
      'Please enter the commit message for your changes above. Lines starting '
      'with \'#\' will be ignored, and an empty message aborts the commit.',
      cf.write)
  pprint.msg('These are the files that will be commited:', cf.write)
  pprint.exp('You can add/remove files to this list', cf.write)
  for f in files:
    pprint.file(f, '', cf.write)
  pprint.sep(cf.write)
  cf.close()
  _launch_vim()
  return _extract_info()


def _launch_vim():
  if subprocess.call('vim %s' % _commit_file(), shell=True) != 0:
    raise Exception('Call to Vim failed')


def _extract_info():
  """Extracts the commit msg and files to commit from the commit file.

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
  # We exhaust the two following lines so that we get to the file list.
  cf.readline()
  cf.readline()

  files = []
  l = cf.readline()
  while l != sep:
    files.append(l[1:].strip())
    l = cf.readline()

  # We reached the separator, this marks the end of the file list.
  return msg, files


def _commit_file():
  return os.path.join(lib.gl_dir(), _COMMIT_FILE)
