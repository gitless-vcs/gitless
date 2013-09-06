# Gitless - a version control system built on top of Git.
# Copyright (c) 2013  Santiago Perez De Rosso.
# Licensed under GNU GPL, version 2.

"""gl resolve - Mark a file with conflicts as resolved."""


from gitless.core import file as file_lib

import pprint


def parser(subparsers):
  """Adds the resolve parser to the given subparsers object."""
  resolve_parser = subparsers.add_parser(
      'resolve', help='mark files with conflicts as resolved')
  resolve_parser.add_argument(
      'files', nargs='+', help='the file(s) in conflict to mark as resolved')
  resolve_parser.set_defaults(func=main)


def main(args):
  success = True

  for fp in args.files:
    ret = file_lib.resolve(fp)
    if ret is file_lib.FILE_NOT_FOUND:
      pprint.err('Can\'t mark as resolved a non-existent file: %s' % fp)
      success = False
    elif ret is file_lib.FILE_NOT_IN_CONFLICT:
      pprint.err('File %s has no conflicts' % fp)
      success = False
    elif ret is file_lib.FILE_ALREADY_RESOLVED:
      pprint.err(
          'Nothing to resolve. File %s was already marked as resolved' % fp)
      success = False
    elif ret is file_lib.SUCCESS:
      pprint.msg('File %s has been marked as resolved' % fp)
    else:
      raise Exception('Unrecognized ret code %s' % ret)

  return success
