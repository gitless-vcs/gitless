# Gitless - a version control system built on top of Git.
# Copyright (c) 2013  Santiago Perez De Rosso.
# Licensed under GNU GPL, version 2.

"""gl resolve - Mark a file with conflicts as resolved."""


import sync_lib

import cmd
import pprint


def parser(subparsers):
  """Adds the resolve parser to the given subparsers object."""
  resolve_parser = subparsers.add_parser(
      'resolve', help='mark files with conflicts as resolved')
  resolve_parser.add_argument(
      'files', nargs='+', help='the file(s) in conflict to mark as resolved')


def main(args):
  cmd.check_gl_dir()
  errors_found = False

  for fp in args.files:
    ret = sync_lib.resolve(fp)
    if ret is sync_lib.FILE_NOT_FOUND:
      pprint.err('Can\'t mark as resolved a non-existent file: %s' % fp)
      errors_found = True
    elif ret is sync_lib.FILE_NOT_IN_CONFLICT:
      pprint.err('File %s has no conflicts' % fp)
      errors_found = True
    elif ret is sync_lib.FILE_ALREADY_RESOLVED:
      pprint.err(
          'Nothing to resolve. File %s was already marked as resolved' % fp)
      errors_found = True
    elif ret is sync_lib.SUCCESS:
      pprint.msg('File %s has been marked as resolved' % fp)
    else:
      raise Exception('Unrecognized ret code %s' % ret)

  return cmd.ERRORS_FOUND if errors_found else cmd.SUCCESS
