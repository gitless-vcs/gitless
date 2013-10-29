# Gitless - a version control system built on top of Git.
# Copyright (c) 2013  Santiago Perez De Rosso.
# Licensed under GNU GPL, version 2.

"""gl init - Create an empty repo or make a clone."""


import os

from gitless.core import repo as repo_lib

import pprint


def parser(subparsers):
  """Adds the init parser to the given subparsers object."""
  init_parser = subparsers.add_parser(
      'init',
      help=(
          'create an empty Gitless\'s repository or create one from an '
          'existing remote repository.'))
  init_parser.add_argument(
      'repo', nargs='?', help='an optional repo path to create the repo from')
  init_parser.set_defaults(func=main)


def main(args):
  if args.repo:
    ret = repo_lib.init_from(args.repo)
  else:
    ret = repo_lib.init_dir()

  #if ret is repo_lib.REPO_UNREACHABLE:
  #  pprint.err('Couldn\'t reach repository %s' % args.repo)
  #  pprint.err_exp('make sure you are connected to the internet')
  #  pprint.err_exp('make sure you have the necessary permissions')
  #  return cmd.ERRORS_FOUND
  if ret is repo_lib.NOTHING_TO_INIT:
    pprint.err('Nothing to init, this directory is already a Gitless\'s repo')
    return False
  elif ret is repo_lib.SUCCESS:
    pprint.msg('Local repo created in {}'.format(os.getcwd()))
    return True
  else:
    raise Exception('Unexpected return code %s' % ret)
