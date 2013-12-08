# Gitless - a version control system built on top of Git.
# Copyright (c) 2013  Santiago Perez De Rosso.
# Licensed under GNU GPL, version 2.

"""gl checkout - Checkout committed versions of files."""


from gitless.core import file as file_lib

import pprint


def parser(subparsers):
  """Adds the checkout parser to the given subparsers object."""
  checkout_parser = subparsers.add_parser(
      'checkout', help='checkout committed versions of files')
  checkout_parser.add_argument(
      '-cp', '--commit_point', help=(
          'the commit point to checkout the files at. Defaults to HEAD.'),
      dest='cp', default='HEAD')
  checkout_parser.add_argument(
      'files', nargs='+', help='the file(s) to checkout')
  checkout_parser.set_defaults(func=main)


def main(args):
  success = True

  for fp in args.files:
    if not _checkout_file(fp, args.cp):
      success = False

  return success


def _checkout_file(fp, cp):
  """Checkout file fp at commit point cp.

  Will output to screen if some error is encountered.

  Returns:
    True if the file was checkouted successfully or False if some error was
    encountered.
  """
  conf_msg = (
      'You have uncomitted changes in %s that could be overwritten by the '
      'checkout' % fp)
  f = file_lib.status(fp)
  if f.type == file_lib.TRACKED and f.modified and not pprint.conf_dialog(
      conf_msg):
    pprint.err('Checkout aborted')
    return False

  ret, out = file_lib.checkout(fp, cp)
  if ret == file_lib.FILE_NOT_FOUND_AT_CP:
    pprint.err('Checkout aborted')
    pprint.err('There\'s no file %s at %s' % (fp, cp))
    return False
  elif ret == file_lib.FILE_IS_DIR:
    pprint.dir_err_exp(fp, subcmd)
    return False
  elif ret == file_lib.SUCCESS:
    pprint.msg('File %s checked out sucessfully to its state at %s' % (fp, cp))
    return True
  else:
    raise Exception('Unrecognized ret code %s' % ret)
