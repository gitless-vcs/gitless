#!/usr/bin/python

"""gl-checkout - Checkout commited versions of files.

Implements the gl-checkout command, part of the Gitless suite.
"""

import argparse
import os

import cmd
import lib
import pprint


def main():
  parser = argparse.ArgumentParser(
      description='Checkout files.')
  parser.add_argument(
      'commit_point', help='the commit point to checkout the files at')
  parser.add_argument(
      'files', nargs='+',
      help='the file(s) to checkout')
  args = parser.parse_args()
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
  ret, out = lib.checkout(fp, cp)
  if ret is lib.FILE_NOT_FOUND_AT_CP:
    pprint.err('There\'s no file %s at %s' % (fp, cp))
    return False
  elif ret is lib.SUCCESS:
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
