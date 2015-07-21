# -*- coding: utf-8 -*-
# Gitless - a version control system built on top of Git.
# Licensed under GNU GPL v2.

"""gl merge - Merge the divergent changes of one branch onto another."""


from __future__ import unicode_literals


from . import helpers, pprint


def parser(subparsers, repo):
  merge_parser = subparsers.add_parser(
      'merge', help='merge the divergent changes of one branch onto another')
  group = merge_parser.add_mutually_exclusive_group()
  group.add_argument(
      'src', nargs='?', help='the source branch to read changes from')
  group.add_argument(
      '-a', '--abort', help='abort the merge in progress', action='store_true')
  merge_parser.set_defaults(func=main)


def main(args, repo):
  current_b = repo.current_branch
  if args.abort:
    current_b.abort_merge()
    pprint.ok('Merge aborted successfully')
    return True

  current_b.merge(helpers.get_branch_or_use_upstream(args.src, 'src', repo))
  pprint.ok('Merge succeeded')
  return True
