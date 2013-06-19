#!/usr/bin/python

"""gl-resolve - Mark a file with conflicts as resolved.

Implements the gl-resolve command, part of the Gitless suite.
"""

import argparse

import cmd
import sync_lib


def main():
  parser = argparse.ArgumentParser(
      description='Mark a file with conflicts as resolved')
  parser.add_argument(
      'files', nargs='+', help='the file(s) in conflict to mark as resolve.')
  args = parser.parse_args()
  for fp in args.files:
    ret = sync_lib.resolve(fp)
    if ret is sync_lib.FILE_NOT_FOUND:
      print 'Can\'t mark as resolved an inexistent file: %s' % fp
    elif ret is sync_lib.FILE_NOT_IN_CONFLICT:
      print 'File %s has no conflicts' % fp
    elif ret is sync_lib.SUCCESS:
      print 'File %s has been marked as resolved' % fp
    else:
      raise Exception('Unexpected return code')


if __name__ == '__main__':
  cmd.run(main)
