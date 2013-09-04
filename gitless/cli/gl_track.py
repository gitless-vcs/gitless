# Gitless - a version control system built on top of Git.
# Copyright (c) 2013  Santiago Perez De Rosso.
# Licensed under GNU GPL, version 2.

"""gl track - Start tracking changes to files."""


from gitless.core import file as file_lib

import cmd
import pprint


def parser(subparsers):
  """Adds the track parser to the given subparsers object."""
  track_parser = subparsers.add_parser(
      'track', help='start tracking changes to files')
  track_parser.add_argument(
      'files', nargs='+', help='the file(s) to track')
  track_parser.set_defaults(func=main)


def main(args):
  cmd.check_gl_dir()
  errors_found = False

  for fp in args.files:
    ret = file_lib.track(fp)
    if ret is file_lib.FILE_NOT_FOUND:
      pprint.err('Can\'t track a non-existent file: %s' % fp)
      errors_found = True
    elif ret is file_lib.FILE_ALREADY_TRACKED:
      pprint.err('File %s is already tracked' % fp)
      errors_found = True
    elif ret is file_lib.FILE_IS_IGNORED:
      pprint.err('File %s is ignored' % fp)
      pprint.err_exp('edit the .gitignore file to stop ignoring file %s' % fp)
    elif ret is file_lib.SUCCESS:
      pprint.msg('File %s is now a tracked file' % fp)
    else:
      raise Exception('Unexpected return code')

  return cmd.ERRORS_FOUND if errors_found else cmd.SUCCESS
