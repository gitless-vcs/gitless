#!/usr/bin/env python2.7

# Gitless - a version control system built on top of Git.
# Copyright (c) 2013  Santiago Perez De Rosso.
# Licensed under GNU GPL, version 2.

"""gl-track - Start tracking changes to files.

Implements the gl-track command, part of the Gitless suite. The gl-track
command allows the user to start tracking changes to the files passed as
parameters.
"""


import check_pyversion

import argparse

import cmd
import lib
import pprint


def main():
  parser = argparse.ArgumentParser(
      description='Start tracking changes to files')
  parser.add_argument(
      'files', nargs='+', help='the file(s) to track')
  args = parser.parse_args()
  errors_found = False

  for fp in args.files:
    ret = lib.track_file(fp)
    if ret is lib.FILE_NOT_FOUND:
      pprint.err('Can\'t track an inexistent file: %s' % fp)
      errors_found = True
    elif ret is lib.FILE_ALREADY_TRACKED:
      pprint.err('File %s is already tracked' % fp)
      errors_found = True
    elif ret is lib.FILE_IS_IGNORED:
      pprint.err('File %s is ignored' % fp)
      pprint.err_exp('edit the .gitignore file to stop ignoring file %s' % fp)
    elif ret is lib.SUCCESS:
      pprint.msg('File %s is now a tracked file' % fp)
    else:
      raise Exception('Unexpected return code')

  return cmd.ERRORS_FOUND if errors_found else cmd.SUCCESS


if __name__ == '__main__':
  cmd.run(main)
