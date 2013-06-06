#!/usr/bin/python

"""gl-untrack - Stop tracking changes to files.

Implements the gl-untrack command, part of the Gitless suite. The gl-untrack
command allows the user to stop tracking changes to the files passed as
parameters."""

import argparse

import lib

def main():
  parser = argparse.ArgumentParser(
      description="Stop tracking changes to files")
  parser.add_argument(
      "file_pattern",
      help="a file_pattern representing the file(s) to untrack")
  args = parser.parse_args()
  ret = lib.untrack_file(args.file_pattern)
  if ret is lib.FILE_NOT_FOUND:
    print 'Can\'t untrack an inexistent file: %s' % args.file_pattern
  elif ret is lib.FILE_ALREADY_UNTRACKED:
    print 'File %s is already untracked' % args.file_pattern
  elif ret is lib.SUCCESS:
    print 'File %s is now a untracked file' % args.file_pattern
  else:
    raise Exception('Unexpected return code')


if __name__ == '__main__':
  main()
