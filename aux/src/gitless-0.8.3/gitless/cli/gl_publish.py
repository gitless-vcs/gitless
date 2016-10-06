# -*- coding: utf-8 -*-
# Gitless - a version control system built on top of Git.
# Licensed under GNU GPL v2.

"""gl publish - Publish commits upstream."""


from __future__ import unicode_literals

from . import helpers, pprint


def parser(subparsers, _):
  """Adds the publish parser to the given subparsers object."""
  desc = 'publish commits upstream'
  publish_parser = subparsers.add_parser(
      'publish', help=desc, description=desc.capitalize())
  publish_parser.add_argument(
      'dst', nargs='?', help='the branch where to publish commits')
  publish_parser.set_defaults(func=main)


def main(args, repo):
  current_b = repo.current_branch
  current_b.publish(helpers.get_branch_or_use_upstream(args.dst, 'dst', repo))
  pprint.ok('Publish succeeded')
  return True
