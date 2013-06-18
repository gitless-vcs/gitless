#!/usr/bin/python

"""gl-rm - rm gitless's files.

Implements the gl-rm command, part of the Gitless suite.
"""

import argparse

import cmd
import lib


def main():
  parser = argparse.ArgumentParser(
      description='Remove tracked files')
  parser.add_argument(
      'files', nargs='+',
      help='a file_pattern representing the file(s) to remove')
  args = parser.parse_args()
  for fp in args.files:
    ret = lib.rm(fp)
    if ret is lib.FILE_NOT_FOUND:
      print 'Can\'t remove an inexistent file: %s' % fp
    elif ret is lib.FILE_IS_UNTRACKED:
      print 'File %s is an untracked file' % fp
    elif ret is lib.SUCCESS:
      print 'File %s has been removed' % fp
    else:
      raise Exception('Unexpected return code')


if __name__ == '__main__':
  cmd.run(main)
