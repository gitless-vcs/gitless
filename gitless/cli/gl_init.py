# -*- coding: utf-8 -*-
# Gitless - a version control system built on top of Git
# Licensed under MIT

"""gl init - Create an empty repo or make a clone."""


from __future__ import unicode_literals

import os

from gitless import core

from . import pprint


def parser(subparsers, _):
  """Adds the init parser to the given subparsers object."""
  desc = (
      'create an empty git repository or clone remote')
  init_parser = subparsers.add_parser(
      'init', help=desc, description=desc.capitalize())
  init_parser.add_argument(
      'repo', nargs='?',
      help=(
          'an optional remote repo address from where to read to create the '
          'local repo'))
  init_parser.add_argument(
      '-o', '--only', nargs='*',
      help='use only branches given from remote repo', dest='only')
  init_parser.add_argument(
      '-e', '--exclude', nargs='+',
      help = 'use everything but this branches from remote repo', dest='exclude')

  init_parser.set_defaults(func=main)


def main(args, repo):
  if repo:
    pprint.err('You are already in a Gitless repository')
    return False
  core.init_repository(url=args.repo,
        only=frozenset(args.only if args.only else []),
        exclude=frozenset(args.exclude if args.exclude else []))
  pprint.ok('Local repo created in {0}'.format(os.getcwd()))
  if args.repo:
    pprint.ok('Initialized from remote {0}'.format(args.repo))
  return True
