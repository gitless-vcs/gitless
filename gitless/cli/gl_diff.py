# Gitless - a version control system built on top of Git.
# Copyright (c) 2013  Santiago Perez De Rosso.
# Licensed under GNU GPL, version 2.

"""gl diff - Show changes in files."""


import os
import subprocess
import tempfile

from gitless.core import file as file_lib

import pprint


def parser(subparsers):
  """Adds the diff parser to the given subparsers object."""
  diff_parser = subparsers.add_parser(
      'diff', help='show changes in files')
  diff_parser.add_argument(
      'files', nargs='*', help='the files to diff')
  diff_parser.set_defaults(func=main)


def main(args):
  if not args.files:
    # Tracked modified files.
    files = [
        f.fp for f in file_lib.status_all() if f.type == file_lib.TRACKED
        and f.modified]
    if not files:
      pprint.msg(
          'Nothing to diff (there are no tracked files with modifications).')
      return True
  else:
    files = args.files

  success = True
  for fp in files:
    ret, out = file_lib.diff(fp)

    if ret is file_lib.FILE_NOT_FOUND:
      pprint.err('Can\'t diff a non-existent file: %s' % fp)
      success = False
    elif ret is file_lib.FILE_IS_UNTRACKED:
      pprint.err(
          'You tried to diff untracked file %s. It\'s probably a mistake. If '
          'you really care about changes in this file you should start '
          'tracking changes to it with gl track %s' % (fp, fp))
      success = False
    elif ret is file_lib.SUCCESS:
      tf = tempfile.NamedTemporaryFile(delete=False)
      pprint.msg(
          'Diff of file %s with its last committed version' % fp, p=tf.write)
      pprint.exp(
          'lines starting with \'-\' are lines that are not in the working '
          'version but that are present in the last committed version of the '
          'file', p=tf.write)
      pprint.exp(
          'lines starting with \'+\' are lines that are in the working version '
          'but not in the last committed version of the file', p=tf.write)
      pprint.blank(p=tf.write)
      tf.write(out)
      tf.close()
      subprocess.call('less -r %s' % tf.name, shell=True)
      os.remove(tf.name)
    else:
      raise Exception('Unrecognized ret code %s' % ret)

  return success
