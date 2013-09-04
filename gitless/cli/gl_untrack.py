# Gitless - a version control system built on top of Git.
# Copyright (c) 2013  Santiago Perez De Rosso.
# Licensed under GNU GPL, version 2.

"""gl untrack - Stop tracking changes to files."""


from gitless.core import file as file_lib

import pprint


def parser(subparsers):
  """Adds the untrack parser to the given subparsers object."""
  untrack_parser = subparsers.add_parser(
      'untrack', help='stop tracking changes to files')
  untrack_parser.add_argument(
      'files', nargs='+', help='the file(s) to untrack')
  untrack_parser.set_defaults(func=main)


def main(args):
  success = True

  for fp in args.files:
    ret = file_lib.untrack(fp)
    if ret is file_lib.FILE_NOT_FOUND:
      pprint.err('Can\'t untrack a non-existent file: %s' % fp)
      success = False
    elif ret is file_lib.FILE_ALREADY_UNTRACKED:
      pprint.err('File %s is already untracked' % fp)
      success = False
    elif ret is file_lib.FILE_IS_IGNORED:
      pprint.err('File %s is ignored. Nothing to untrack' % fp)
      pprint.err_exp('edit the .gitignore file to stop ignoring file %s' % fp)
      success = False
    elif ret is file_lib.SUCCESS:
      pprint.msg('File %s is now an untracked file' % fp)
    elif ret is file_lib.FILE_IN_CONFLICT:
      pprint.err('Can\'t untrack a file in conflict')
      success = False
    else:
      raise Exception('Unexpected return code')

  return success
