#!/usr/bin/env python2.7

# Gitless - a version control system built on top of Git.
# Copyright (c) 2013  Santiago Perez De Rosso.
# Licensed under GNU GPL, version 2.

"""gl-rm - Remove Gitless's files.

Implements the gl-rm command, part of the Gitless suite.
"""


import check_pyversion

import argparse

import file_lib

import cmd
import pprint


def main():
  parser = argparse.ArgumentParser(
      description='Remove tracked files')
  parser.add_argument(
      'files', nargs='+', help='the file(s) to remove')
  args = parser.parse_args()
  errors_found = False

  for fp in args.files:
    ret = file_lib.rm(fp)
    if ret is file_lib.FILE_NOT_FOUND:
      pprint.err('Can\'t remove a non-existent file: %s' % fp)
      errors_found = True
    elif ret is file_lib.FILE_IS_UNTRACKED:
      pprint.err('File %s is an untracked file' % fp)
      errors_found = True
    elif ret is file_lib.SUCCESS:
      pprint.msg('File %s has been removed' % fp)
    else:
      raise Exception('Unexpected return code')

  return cmd.ERRORS_FOUND if errors_found else cmd.SUCCESS


if __name__ == '__main__':
  cmd.run(main)
