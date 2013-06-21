#!/usr/bin/python

"""gl-rebase - Rebase one branch onto another.

Implements the gl-rebase command, part of the Gitless suite.
"""

import argparse
import sys

import cmd
import pprint
import sync_lib


def main():
  parser = argparse.ArgumentParser(
      description=(
        'Converge divergent changes of two branches by rebasing one onto '
        'another'))
  parser.add_argument('src', nargs='?', help=(
    'the source branch to use as a base for rebasing'))
  parser.add_argument(
      '-a', '--abort', help='abort the rebase in progress', action='store_true')
  args = parser.parse_args()


  if args.abort:
    if sync_lib.abort_rebase() is sync_lib.REBASE_NOT_IN_PROGRESS:
      pprint.msg('No rebase in progress, nothing to abort')
      pprint.exp(
          'To converge divergent changes of the current branch and branch b by '
          'rebasing the current branch out of b do gl rebase <b>')
    else:
     pprint.msg('Rebase aborted')
    return

  if not args.src:
    parser.error('No src branch specified')

  ret, out = sync_lib.rebase(args.src)
  if ret is sync_lib.SRC_NOT_FOUND:
    pprint.msg('Branch %s not found' % args.src, sys.stdout.write)
    pprint.exp('do gl branch to list all existing branches', sys.stdout.write)
  elif ret is sync_lib.SRC_IS_CURRENT_BRANCH:
    pprint.msg('Branch %s is the current branch' % args.src, sys.stdout.write)
    pprint.exp(
        'to rebase branch %s onto another branch b, do gl branch b, and gl '
        'rebase  %s from there' % (args.src, args.src), sys.stdout.write)
  elif ret is sync_lib.CONFLICT:
    pprint.msg('There are conflicts you need to resolve')
    pprint.exp(
        'edit the files in conflict and do gl resolve <f> to mark file f as '
        'resolved')
    pprint.exp(
        'once all conflicts have been resolved do gl commit to commit the '
        'changes and continue rebasing')
    pprint.blank()
    pprint.msg('Files in conflict:')
    for f in out:
      pprint.file(f, '')
  elif ret is sync_lib.NOTHING_TO_REBASE:
    pprint.msg(
        'No divergent changes to rebase from %s' % args.src, sys.stdout.write)
 # elif ret is sync_lib.LOCAL_CHANGES_WOULD_BE_LOST:
 #   pprint.msg(
 #       'Rebase was aborted because your local changes to the following files '
 #       'would be overwritten by merge:', sys.stdout.write)
 #   pprint.exp('use gl commit to commit your changes', sys.stdout.write)
 #   pprint.exp(
 #       'use gl checkout HEAD f to discard changes to tracked file f',
 #       sys.stdout.write)
 #   for fp in out:
 #     pprint.file(fp, '', sys.stdout.write)




if __name__ == '__main__':
  cmd.run(main)
