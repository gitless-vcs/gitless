# -*- coding: utf-8 -*-
# Gitless - a version control system built on top of Git.
# Licensed under GNU GPL v2.

"""gl switch - Switch branches."""


from __future__ import unicode_literals

from . import pprint


def parser(subparsers, _):
  """Adds the switch parser to the given subparsers object."""
  desc = 'switch branches'
  switch_parser = subparsers.add_parser(
      'switch', help=desc, description=desc.capitalize())
  switch_parser.add_argument('branch', help='switch to branch')
  switch_parser.add_argument(
      '-mo', '--move-over',
      help='move uncomitted changes made in the current branch to the '
      'destination branch',
      action='store_true')
  switch_parser.set_defaults(func=main)


def main(args, repo):
  b = repo.lookup_branch(args.branch)

  if not b:
    pprint.err('Branch {0} doesn\'t exist'.format(args.branch))
    pprint.err_exp('to list existing branches do gl branch')
    return False

  repo.switch_current_branch(b, move_over=args.move_over)
  pprint.ok('Switched to branch {0}'.format(args.branch))
  return True
