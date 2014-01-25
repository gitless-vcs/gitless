# Gitless - a version control system built on top of Git.
# Copyright (c) 2013  Santiago Perez De Rosso.
# Licensed under GNU GPL, version 2.

"""gl init - Create an empty repo or make a clone."""


import os

from gitless.core import init as init_lib

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
  ret = init_lib.init_from(args.repo) if args.repo else init_lib.init_cwd()

  if ret == init_lib.REPO_UNREACHABLE:
    pprint.err(
        'Couldn\'t reach remote repository \'{}\' to init from'.format(
            args.repo))
    pprint.err_exp('make sure you are connected to the internet')
    pprint.err_exp(
        'make sure you have the necessary permissions to access {}'.format(
            args.repo))
    return False
  if ret is init_lib.NOTHING_TO_INIT:
    pprint.err('Nothing to init, this directory is already a Gitless\'s repo')
    return False
  elif ret is init_lib.SUCCESS:
    pprint.msg('Local repo created in \'{}\''.format(os.getcwd()))
    if args.repo:
      pprint.msg('Initialized from remote \'{}\''.format(args.repo))
    return True
  else:
    raise Exception('Unexpected return code %s' % ret)
