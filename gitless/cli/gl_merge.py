# -*- coding: utf-8 -*-
# Gitless - a version control system built on top of Git.
# Licensed under GNU GPL v2.

"""gl merge - Merge the divergent changes of one branch onto another."""


from __future__ import unicode_literals

from gitless import core

from . import helpers, pprint


def parser(subparsers, repo):
  desc = 'merge the divergent changes of one branch onto another'
  merge_parser = subparsers.add_parser(
      'merge', help=desc, description=desc.capitalize())
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

  src_branch = helpers.get_branch_or_use_upstream(args.src, 'src', repo)
  try:
    current_b.merge(src_branch, op_cb=pprint.OP_CB)
    pprint.ok('Merge succeeded')
  except core.ApplyFailedError as e:
    pprint.ok('Merge succeeded')
    raise e
  return True
