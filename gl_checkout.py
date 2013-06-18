#!/usr/bin/python

"""gl-checkout - Checkout commited versions of files.

Implements the gl-checkout command, part of the Gitless suite.
"""

import argparse
import os

import cmd
import lib


def main():
  parser = argparse.ArgumentParser(
      description='Checkout files.')
  parser.add_argument(
      'commit_point', help='the commit point to checkout the files at')
  parser.add_argument(
      'files', nargs='+',
      help='a file_pattern representing the file(s) to checkout')
  args = parser.parse_args()
  cp = args.commit_point
  for fp in args.files:
    _checkout_file(fp, cp)


def _checkout_file(fp, cp):
  """Checkout file fp to commit point cp.
  
  Will output to screen if some error is encountered.
  """
  ret, out = lib.checkout(fp, cp)
  if ret is lib.FILE_NOT_FOUND_AT_CP:
    print 'There\'s no file %s at %s' % (fp, cp)
  elif ret is lib.SUCCESS:
    # TODO(sperezde): show conf dialog here if the file exists.
    dst = open(fp, 'w')
    dst.write(out)
    dst.close()
    print 'File %s checked out sucessfully to its state at %s' % (fp, cp)
  else:
    raise Exception('Unrecognized ret code %s' % ret)


if __name__ == '__main__':
  cmd.run(main)
