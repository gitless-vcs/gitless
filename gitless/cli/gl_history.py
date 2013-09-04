# Gitless - a version control system built on top of Git.
# Copyright (c) 2013  Santiago Perez De Rosso.
# Licensed under GNU GPL, version 2.

"""gl history - Show commit history."""


from gitless.core import history as history_lib


def parser(subparsers):
  """Adds the history parser to the given subparsers object."""
  history_parser = subparsers.add_parser(
      'history', help='show commit history')
  history_parser.add_argument(
      '-v', '--verbose', help='be verbose, will output the diffs of the commit',
      action='store_true')
  history_parser.set_defaults(func=main)


def main(args):
  history_lib.show(verbose=args.verbose)
  return True
