# -*- coding: utf-8 -*-
# Gitless - a version control system built on top of Git.
# Licensed under GNU GPL v2.

"""Helper for gl_{merge, rebase}."""


from __future__ import unicode_literals

from . import helpers
from . import pprint


def parser(subcmd):
  def f(subparsers, _):
    sync_parser = subparsers.add_parser(
        subcmd,
        help='{0} the divergent changes of one branch onto another'.format(
            subcmd))
    group = sync_parser.add_mutually_exclusive_group()
    group.add_argument(
        'src', nargs='?', help='the source branch to read changes from')
    group.add_argument(
        '-a', '--abort', help='abort the {0} in progress'.format(subcmd),
        action='store_true')
    sync_parser.set_defaults(func=main(subcmd))
  return f


def main(subcmd):
  def f(args, repo):
    current_b = repo.current_branch
    if args.abort:
      if subcmd == 'merge':
        current_b.abort_merge()
      else:
        current_b.abort_rebase()

      pprint.ok('{0} aborted successfully'.format(subcmd.capitalize()))
      return True

    src_branch = None
    if not args.src:
      # We use the upstream branch, if any.
      if not current_b.upstream:
        pprint.err(
            'No src branch specified and the current branch has no upstream '
            'branch set')
        return False
      src_branch = current_b.upstream
      pprint.msg(
          'No src branch specified, defaulted to getting changes from upstream '
          'branch {0}'.format(helpers.get_branch_name(src_branch)))
    else:
      src_branch = helpers.get_branch(args.src, repo)

    if subcmd == 'merge':
      current_b.merge(src_branch)
    else:
      current_b.rebase(src_branch)
    pprint.ok('{0} succeeded'.format(subcmd.capitalize()))
    return True
  return f
