# Gitless - a version control system built on top of Git.
# Copyright (c) 2013  Santiago Perez De Rosso.
# Licensed under GNU GPL, version 2.

"""gl checkout - Checkout committed versions of files."""


import os

import file_lib

import cmd
import pprint


def parser(subparsers):
  """Adds the checkout parser to the given subparsers object."""
  checkout_parser = subparsers.add_parser(
      'checkout', help='checkout committed versions of files')
  checkout_parser.add_argument(
      'commit_point', help='the commit point to checkout the files at')
  checkout_parser.add_argument(
      'files', nargs='+', help='the file(s) to checkout')
  checkout_parser.set_defaults(func=main)


def main(args):
  cmd.check_gl_dir()

  cp = args.commit_point
  errors_found = False

  for fp in args.files:
    if not _checkout_file(fp, cp):
      errors_found = True

  return cmd.ERRORS_FOUND if errors_found else cmd.SUCCESS


def _checkout_file(fp, cp):
  """Checkout file fp to commit point cp.

  Will output to screen if some error is encountered.

  Returns:
    True if the file was checkouted successfuly or False if some error was
    encountered.
  """
  ret, out = file_lib.checkout(fp, cp)
  if ret is file_lib.FILE_NOT_FOUND_AT_CP:
    pprint.err('There\'s no file %s at %s' % (fp, cp))
    return False
  elif ret is file_lib.SUCCESS:
    # TODO(sperezde): show conf dialog here if the file exists.
    # dst = open(fp, 'w')
    # dst.write(out)
    # dst.close()
    pprint.msg('File %s checked out sucessfully to its state at %s' % (fp, cp))
    return True
  else:
    raise Exception('Unrecognized ret code %s' % ret)


if __name__ == '__main__':
  cmd.run(main)
