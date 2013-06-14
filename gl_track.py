#!/usr/bin/python

"""gl-track - Start tracking changes to files.

Implements the gl-track command, part of the Gitless suite. The gl-track
command allows the user to start tracking changes to the files passed as
parameters.
"""

import argparse

import cmd
import lib


def main():
  parser = argparse.ArgumentParser(
      description="Start tracking changes to files")
  parser.add_argument(
      "file_pattern", help="a file_pattern representing the file(s) to track")
  args = parser.parse_args()
  ret = lib.track_file(args.file_pattern)
  if ret is lib.FILE_NOT_FOUND:
    print 'Can\'t track an inexistent file: %s' % args.file_pattern
  elif ret is lib.FILE_ALREADY_TRACKED:
    print 'File %s is already tracked' % args.file_pattern
  elif ret is lib.SUCCESS:
    print 'File %s is now a tracked file' % args.file_pattern
  else:
    raise Exception('Unexpected return code')


if __name__ == '__main__':
  cmd.run(main)
