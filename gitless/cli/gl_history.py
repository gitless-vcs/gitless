# -*- coding: utf-8 -*-
# Gitless - a version control system built on top of Git.
# Licensed under GNU GPL v2.

"""gl history - Show commit history."""


from __future__ import unicode_literals

import os
import tempfile

from . import helpers, pprint


def parser(subparsers, _):
  """Adds the history parser to the given subparsers object."""
  desc = 'show commit history'
  history_parser = subparsers.add_parser(
      'history', help=desc, description=desc.capitalize())
  history_parser.add_argument(
      '-v', '--verbose', help='be verbose, will output the diffs of the commit',
      action='store_true')
  history_parser.add_argument(
      '-l', '--limit', help='limit number of commits displayed', type=int)
  history_parser.add_argument(
      '-c', '--compact', help='output history in a compact format',
      action='store_true', default=False)
  history_parser.add_argument(
      '-b', '--branch', nargs='?', metavar='branch_name', dest='b',
      help='the branch to show history of (defaults to the current branch)')
  history_parser.set_defaults(func=main)


def main(args, repo):
  b = helpers.get_branch(args.b, repo) if args.b else repo.current_branch
  with tempfile.NamedTemporaryFile(mode='w', delete=False) as tf:
    count = 0
    for ci in b.history():
      if args.limit and count == args.limit:
        break
      pprint.commit(ci, compact=args.compact, stream=tf.write)
      if not args.compact:
        pprint.puts(stream=tf.write)
      if args.verbose and len(ci.parents) == 1:
        for patch in b.diff_commits(ci.parents[0], ci):
          pprint.diff(patch, stream=tf.write)

      count += 1
  helpers.page(tf.name, repo)
  os.remove(tf.name)
  return True
