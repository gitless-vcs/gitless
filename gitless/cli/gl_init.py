# Gitless - a version control system built on top of Git.
# Licensed under GNU GPL v2.

"""gl init - Create an empty repo or make a clone."""


import os

from gitless.core import core

from . import pprint


def parser(subparsers):
  """Adds the init parser to the given subparsers object."""
  init_parser = subparsers.add_parser(
      'init',
      help=(
          'create an empty Gitless\'s repository or create one from an '
          'existing remote repository.'))
  init_parser.add_argument(
      'repo', nargs='?',
      help=(
          'an optional remote repo address from where to read to create the'
          'local repo.'))
  init_parser.set_defaults(func=main)


def main(args):
  core.init_repository(url=args.repo)
  pprint.msg('Local repo created in \'{0}\''.format(os.getcwd()))
  if args.repo:
    pprint.msg('Initialized from remote \'{0}\''.format(args.repo))
  return True
