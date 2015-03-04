# Gitless - a version control system built on top of Git.
# Licensed under GNU GPL v2.

"""gl checkout - Checkout committed versions of files."""


import os

import gitless.core.core as core

from . import pprint


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


def main(args, repo):
  success = True
  for fp in args.files:
    if not _checkout_file(fp, args.cp, repo):
      success = False

  return success


def _checkout_file(fp, cp, repo):
  """Checkout file fp at commit point cp.

  Will output to screen if some error is encountered.

  Returns:
    True if the file was checkouted successfully or False if some error was
    encountered.
  """
  curr_b = repo.current_branch
  conf_msg = (
      'You have uncomitted changes in {0} that could be overwritten by the '
      'checkout'.format(fp))

  try:
    f = curr_b.status_file(os.path.relpath(fp, repo.root))
    if f.type == core.GL_STATUS_TRACKED and f.modified and (
        not pprint.conf_dialog(conf_msg)):
      pprint.err('Checkout aborted')
      return False
  except KeyError:
    pass

  try:
    curr_b.checkout_file(fp, repo.revparse_single(cp))
    pprint.msg(
        'File {0} checked out sucessfully to its state at {1}'.format(fp, cp))
    return True
  except KeyError:
    pprint.err('Checkout aborted')
    pprint.err('There\'s no file {0} at {1}'.format(fp, cp))
    return False
