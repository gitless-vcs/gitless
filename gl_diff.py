#!/usr/bin/env python2.7

# Gitless - a version control system built on top of Git.
# Copyright (c) 2013  Santiago Perez De Rosso.
# Licensed under GNU GPL, version 2.

"""gl-diff - Show changes in files.

Implements the gl-diff command, part of the Gitless suite. The gl-diff command
allows the user to show the difference between the current version of a file and
its version in the repo.
"""


import check_pyversion

import argparse
import os
import subprocess
import tempfile

import cmd
import lib
import pprint


def main():
  parser = argparse.ArgumentParser(
      description='Show changes in files')
  parser.add_argument(
      'files', nargs='+', help='the files to diff')
  args = parser.parse_args()
  errors_found = False

  for fp in args.files:
    ret, out = lib.diff(fp)

    if ret is lib.FILE_NOT_FOUND:
      pprint.err('Can\'t diff an inexistent file: %s' % fp)
      errors_found = True
    elif ret is lib.FILE_IS_UNTRACKED:
      pprint.err(
          'You tried to diff untracked file %s. It\'s probably a mistake. If '
          'you really care about changes in this file you should start '
          'tracking changes to it with gl track %s' % (fp, fp))
      errors_found = True
    elif ret is lib.SUCCESS:
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
      subprocess.call('less %s' % tf.name, shell=True)
      os.remove(tf.name)
    else:
      raise Exception('Unrecognized ret code %s' % ret)

  return cmd.ERRORS_FOUND if errors_found else cmd.SUCCESS


if __name__ == '__main__':
  cmd.run(main)
