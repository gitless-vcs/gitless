# -*- coding: utf-8 -*-
# Gitless - a version control system built on top of Git.
# Licensed under GNU GPL v2.

"""gl fuse - Fuse the divergent changes of a branch onto the current branch."""


from __future__ import unicode_literals

from gitless import core

from . import helpers, pprint


def parser(subparsers, repo):
  desc = 'fuse the divergent changes of a branch onto the current branch'
  fuse_parser = subparsers.add_parser(
      'fuse', help=desc, description=(
        desc.capitalize() + '. ' +
        'By default all divergent changes from the given source branch are '
        'fused. To customize the set of commmits to fuse use the only and '
        'exclude flags'))
  fuse_parser.add_argument(
      'src', nargs='?',
      help=(
        'the source branch to read changes from. If none is given the upstream '
        'branch of the current branch is used as the source'))
  fuse_parser.add_argument(
      '-o', '--only', nargs='+',
      help=(
        'fuse only the commits given (commits must belong to the set of '
        'divergent commits from the given src branch)'),
      metavar='commit_id', action=helpers.CommitIdProcessor, repo=repo)
  fuse_parser.add_argument(
      '-e', '--exclude', nargs='+',
      help=(
        'exclude from the fuse the commits given (commits must belong to the '
        'set of divergent commits from the given src branch)'),
      metavar='commit_id', action=helpers.CommitIdProcessor, repo=repo)
  fuse_parser.add_argument(
      '-ip', '--insertion-point', nargs='?',
      help=(
        'the divergent changes will be inserted after the commit given, dp for '
        'divergent point is the default'), metavar='commit_id')
  fuse_parser.add_argument(
      '-a', '--abort', help='abort the fuse in progress', action='store_true')
  fuse_parser.set_defaults(func=main)


def main(args, repo):
  current_b = repo.current_branch
  if args.abort:
    current_b.abort_fuse(op_cb=pprint.OP_CB)
    pprint.ok('Fuse aborted successfully')
    return True

  src_branch = helpers.get_branch_or_use_upstream(args.src, 'src', repo)

  mb = repo.merge_base(current_b, src_branch)
  if mb == src_branch.target:  # the current branch is ahead or both branches are equal
    pprint.err('No commits to fuse')
    return False

  if (not args.insertion_point or args.insertion_point == 'dp' or
      args.insertion_point == 'divergent-point'):
    insertion_point = mb
  else:
    insertion_point = repo.revparse_single(args.insertion_point).id

  def valid_input(inp):
    walker = src_branch.history()
    walker.hide(insertion_point)
    divergent_ids = frozenset(ci.id for ci in walker)

    errors_found = False
    for ci in inp - divergent_ids:
      pprint.err(
          'Commit with id {0} is not among the divergent commits of branch '
          '{1}'.format(ci, src_branch))
      errors_found = True
    return not errors_found

  only = None
  exclude = None
  if args.only:
    only = frozenset(args.only)
    if not valid_input(only):
      return False
  elif args.exclude:
    exclude = frozenset(args.exclude)
    if not valid_input(exclude):
      return False


  try:
    current_b.fuse(
        src_branch, insertion_point, only=only, exclude=exclude,
        op_cb=pprint.OP_CB)
    pprint.ok('Fuse succeeded')
  except core.ApplyFailedError as e:
    pprint.ok('Fuse succeeded')
    raise e
  return True
