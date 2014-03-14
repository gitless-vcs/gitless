# Gitless - a version control system built on top of Git.
# Copyright (c) 2013  Santiago Perez De Rosso.
# Licensed under GNU GPL, version 2.

"""gl diff - Show changes in files."""


import os
import subprocess
import tempfile

from gitless.core import file as file_lib

from . import pprint


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
    ret, (out, padding, additions, deletions) = file_lib.diff(fp)

    if ret == file_lib.FILE_NOT_FOUND:
      pprint.err('Can\'t diff a non-existent file: {0}'.format(fp))
      success = False
    elif ret == file_lib.FILE_IS_UNTRACKED:
      pprint.err(
          'You tried to diff untracked file {0}. It\'s probably a mistake. If '
          'you really care about changes in this file you should start '
          'tracking changes to it with gl track {1}'.format(fp, fp))
      success = False
    elif ret == file_lib.FILE_IS_IGNORED:
      pprint.err(
          'You tried to diff ignored file {0}. It\'s probably a mistake. If '
          'you really care about changes in this file you should stop ignoring '
          'it by editing the .gigignore file'.format(fp))
      success = False
    elif ret == file_lib.FILE_IS_DIR:
      pprint.dir_err_exp(fp, 'diff')
      success = False
    elif ret == file_lib.SUCCESS:
      if not out:
        pprint.msg(
            'The working version of file {0} is the same as its last '
            'committed version. No diffs to output'.format(fp))
        continue

      with tempfile.NamedTemporaryFile(mode='w', delete=False) as tf:
        pprint.msg(
            'Diff of file {0} with its last committed version'.format(fp),
            p=tf.write)
        put_s = lambda num: '' if num == 1 else 's'
        pprint.msg(
            '{0} line{1} added'.format(additions, put_s(additions)), p=tf.write)
        pprint.msg(
            '{0} line{1} removed'.format(deletions, put_s(deletions)),
            p=tf.write)
        pprint.diff(out, padding, p=tf.write)

      subprocess.call('less -r -f {0}'.format(tf.name), shell=True)
      os.remove(tf.name)
    else:
      raise Exception('Unrecognized ret code %s' % ret)

  return success
