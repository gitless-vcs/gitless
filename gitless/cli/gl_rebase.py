# Gitless - a version control system built on top of Git.
# Copyright (c) 2013  Santiago Perez De Rosso.
# Licensed under GNU GPL, version 2.

"""gl rebase - Rebase one branch onto another."""


from gitless.core import branch as branch_lib
from gitless.core import sync as sync_lib

import pprint


def parser(subparsers):
  """Adds the rebase parser to the given subparsers object."""
  rebase_parser = subparsers.add_parser(
      'rebase',
      help=(
          'converge divergent changes of two branches by rebasing one onto '
          'another'))
  group = rebase_parser.add_mutually_exclusive_group()
  group.add_argument(
      'src', nargs='?', help='the source branch to use as a base for rebasing')
  group.add_argument(
      '-a', '--abort', help='abort the rebase in progress', action='store_true')
  group.add_argument(
      '-s', '--skip',
      help='skip the current commit and continue with the next one',
      action='store_true')

  rebase_parser.set_defaults(func=main)


def main(args):
  if args.abort:
    if sync_lib.abort_rebase() is sync_lib.REBASE_NOT_IN_PROGRESS:
      pprint.err('No rebase in progress, nothing to abort')
      pprint.err_exp(
          'To converge divergent changes of the current branch and branch b by '
          'rebasing the current branch out of b do gl rebase <b>')
      return False
    pprint.msg('Rebase aborted')
    return True

  if args.skip:
    if sync_lib.skip_rebase_commit() is sync_lib.REBASE_NOT_IN_PROGRESS:
      pprint.err('No rebase in progress, nothing to skip')
      pprint.err_exp(
          'To converge divergent changes of the current branch and branch b by '
          'rebasing the current branch out of b do gl rebase <b>')
      return False

    pprint.msg('Rebase commit skipped')
    return True

  if not args.src:
    # We use the upstream branch, if any.
    current = branch_lib.current()
    b_st = branch_lib.status(current)
    if b_st.upstream is None:
      pprint.err(
          'No src branch specified and the current branch has no upstream '
          'branch set')
      return False

    if not b_st.upstream_exists:
      pprint.err(
          'Current branch has an upstream set but it hasn\'t been published '
          'yet')
      return False

    # If we reached this point, it is safe to use the upstream branch to get
    # changes from.
    args.src = b_st.upstream
    pprint.msg(
        'No src branch specified, defaulted to getting changes from upstream '
        'branch %s' % args.src)

  if sync_lib.rebase_in_progress():
    pprint.err('You are already in the middle of a rebase')
    pprint.err_exp('use gl rebase --abort to abort the current rebase')
    return False

  ret, out = sync_lib.rebase(args.src)
  if ret is sync_lib.SRC_NOT_FOUND:
    pprint.err('Branch %s not found' % args.src)
    pprint.err_exp('do gl branch to list all existing branches')
    return False
  elif ret is sync_lib.SRC_IS_CURRENT_BRANCH:
    pprint.err('Branch %s is the current branch' % args.src)
    pprint.err_exp(
        'to rebase branch %s onto another branch b, do gl branch b, and gl '
        'rebase %s from there' % (args.src, args.src))
    return False
  elif ret is sync_lib.REMOTE_NOT_FOUND:
    pprint.err('The remote of %s doesn\'t exist' % args.src)
    pprint.err_exp('to list available remotes do gl remote show')
    pprint.err_exp(
        'to add a new remote use gl remote add remote_name remote_url')
    return False
  elif ret is sync_lib.REMOTE_UNREACHABLE:
    pprint.err('Can\'t reach the remote')
    pprint.err_exp('make sure that you are still connected to the internet')
    pprint.err_exp('make sure you still have permissions to access the remote')
    return False
  elif ret is sync_lib.REMOTE_BRANCH_NOT_FOUND:
    pprint.err('The branch doesn\'t exist in the remote')
    return False
  elif ret is sync_lib.CONFLICT:
    pprint.err('There are conflicts you need to resolve')
    pprint.err_exp('use gl status to look at the files in conflict')
    pprint.err_exp(
        'edit the files in conflict and do gl resolve <f> to mark file f as '
        'resolved')
    pprint.err_exp(
        'once all conflicts have been resolved do gl commit to commit the '
        'changes and continue rebasing')
    pprint.err_blank()
    # pprint.err('Files in conflict:')
    # for f in out:
    #  pprint.err_item(f)
    return False
  elif ret is sync_lib.NOTHING_TO_REBASE:
    pprint.err(
        'No divergent changes to rebase from %s' % args.src)
  elif ret is sync_lib.LOCAL_CHANGES_WOULD_BE_LOST:
    pprint.err(
        'Rebase was aborted because you have uncommited local changes')
    pprint.err_exp('use gl commit to commit your changes')
    return False
  elif ret is sync_lib.SUCCESS:
    pprint.msg('Rebase succeded')
    return True
  else:
    raise Exception('Unexpected ret code %s' % ret)
