#!/usr/bin/python

"""gl-untrack - Stop tracking changes to files.

Implements the gl-untrack command, part of the Gitless suite. The gl-untrack
command allows the user to stop tracking changes to the files passed as
parameters."""


import argparse

import cmd
import lib
import pprint


def main():
  parser = argparse.ArgumentParser(
      description='Stop tracking changes to files')
  parser.add_argument(
      'files', nargs='+', help='the file(s) to untrack')
  args = parser.parse_args()
  for fp in args.files:
    ret = lib.untrack_file(fp)
    if ret is lib.FILE_NOT_FOUND:
      pprint.err('Can\'t untrack an inexistent file: %s' % fp)
    elif ret is lib.FILE_ALREADY_UNTRACKED:
      pprint.err('File %s is already untracked' % fp)
    elif ret is lib.SUCCESS:
      pprint.msg('File %s is now a untracked file' % fp)
    else:
      raise Exception('Unexpected return code')


if __name__ == '__main__':
  cmd.run(main)
