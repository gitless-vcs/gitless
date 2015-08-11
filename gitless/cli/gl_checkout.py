# -*- coding: utf-8 -*-
# Gitless - a version control system built on top of Git.
# Licensed under GNU GPL v2.

"""gl checkout - Checkout committed versions of files."""


from __future__ import unicode_literals

from gitless import core

from . import helpers, pprint


def parser(subparsers, repo):
  """Adds the checkout parser to the given subparsers object."""
  desc = 'checkout committed versions of files'
  checkout_parser = subparsers.add_parser(
      'checkout', help=desc, description=desc.capitalize())
  checkout_parser.add_argument(
      '-cp', '--commit-point', help=(
          'the commit point to checkout the files at. Defaults to HEAD.'),
      dest='cp', default='HEAD')
  checkout_parser.add_argument(
      'files', nargs='+', help='the file(s) to checkout',
      action=helpers.PathProcessor, repo=repo)
  checkout_parser.set_defaults(func=main)


def main(args, repo):
  errors_found = False

  curr_b = repo.current_branch
  cp = args.cp

  for fp in args.files:
    conf_msg = (
        'You have uncomitted changes in "{0}" that could be overwritten by '
        'checkout'.format(fp))
    try:
      f = curr_b.status_file(fp)
      if f.type == core.GL_STATUS_TRACKED and f.modified and (
          not pprint.conf_dialog(conf_msg)):
        pprint.err('Checkout aborted')
        continue
    except KeyError:
      pass

    try:
      curr_b.checkout_file(fp, repo.revparse_single(cp))
      pprint.ok(
          'File {0} checked out successfully to its state at {1}'.format(
              fp, cp))
    except KeyError:
      pprint.err('Checkout aborted')
      pprint.err('There\'s no file {0} at {1}'.format(fp, cp))
      errors_found = True

  return not errors_found
