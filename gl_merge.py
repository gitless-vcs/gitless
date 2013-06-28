#!/usr/bin/python

"""gl-merge - Merge the divergent changes of one branch onto another.

Implements the gl-merge command, part of the Gitless suite.
"""

import argparse
import sys

import branch_lib
import cmd
import pprint
import sync_lib


def main():
  parser = argparse.ArgumentParser(
      description='Merge the divergent changes of one branch onto another')
  parser.add_argument('src', nargs='?', help='the source branch to read changes from')
  parser.add_argument('-a', '--abort', help='abort the merge in progress', action='store_true')
  args = parser.parse_args()


  if args.abort:
    if sync_lib.abort_merge() is sync_lib.MERGE_NOT_IN_PROGRESS:
      pprint.err('No merge in progress, nothing to abort')
      pprint.err_exp(
          'To merge divergent changes of branch b onto the current branch do gl'
          ' merge <b>')
      return cmd.ERRORS_FOUND
    pprint.msg('Merge aborted successfully')
    return cmd.SUCCESS

  if not args.src:
    # We use the upstream branch, if any.
    current = branch_lib.current()
    ur, ub = branch_lib.upstream(current)
    if ur is None:
      parser.error(
          'No src branch specified and the current branch has no upstream '
          'branch set')

    if branch_lib.has_unpushed_upstream(current, ur, ub):
        pprint.err(
            'Current branch has an upstream set but it hasn\'t been pushed yet')
        return cmd.ERRORS_FOUND

    # If we reached this point, it is safe to use the upstream branch to get
    # changes from.
    args.src = '/'.join([ur, ub])
    pprint.msg(
        'No src branch specified, defaulted to getting changes from upstream '
        'branch %s' % args.src)


  ret, out = sync_lib.merge(args.src)
  if ret is sync_lib.SRC_NOT_FOUND:
    pprint.err('Branch %s not found' % args.src)
    pprint.err_exp('do gl branch to list all existing branches')
    return cmd.ERRORS_FOUND
  elif ret is sync_lib.SRC_IS_CURRENT_BRANCH:
    pprint.err('Branch %s is the current branch' % args.src)
    pprint.err_exp(
        'to merge branch %s onto another branch b, do gl branch b, and gl merge'
        ' %s from there' % (args.src, args.src))
    return cmd.ERRORS_FOUND
  elif ret is sync_lib.REMOTE_NOT_FOUND:
    pprint.err('The remote of %s doesn\'t exist' % args.src)
    pprint.err_exp('to list available remotes do gl remote show')
    pprint.err_exp(
        'to add a new remote use gl remote add remote_name remote_url')
    return cmd.ERRORS_FOUND
  elif ret is sync_lib.REMOTE_UNREACHABLE:
    pprint.err('Can\'t reach the remote')
    pprint.err_exp('make sure that you are still connected to the internet')
    pprint.err_exp('make sure you still have permissions to access the remote')
    return cmd.ERRORS_FOUND
  elif ret is sync_lib.REMOTE_BRANCH_NOT_FOUND:
    pprint.err('The branch doesn\'t exist in the remote')
    return cmd.ERRORS_FOUND
  elif ret is sync_lib.NOTHING_TO_MERGE:
    pprint.err(
        'No divergent changes to merge from %s' % args.src)
    return cmd.ERRORS_FOUND
  elif ret is sync_lib.LOCAL_CHANGES_WOULD_BE_LOST:
    pprint.err(
        'Merge was aborted because your local changes to the following files '
        'would be overwritten by merge:')
    pprint.err_exp('use gl commit to commit your changes')
    pprint.err_exp(
        'use gl checkout HEAD f to discard changes to tracked file f')
    for fp in out:
      pprint.err_item(fp)
    
    return cmd.ERRORS_FOUND
  elif ret is sync_lib.CONFLICT:
    pprint.err(
        'Merge was aborted becase there are conflicts you need to resolve')
    pprint.err_exp(
        'use gl status to look at the files in conflict')
    pprint.err_exp(
        'use gl merge --abort to go back to the state before the merge')
    pprint.err_exp('use gl resolve <f> to mark file f as resolved')
    pprint.err_exp(
        'once you solved all conflicts do gl commit to complete the merge')
    return cmd.ERRORS_FOUND
  elif ret is sync_lib.SUCCESS:
    pprint.msg('Merged succeeded')

  return cmd.SUCCESS


if __name__ == '__main__':
  cmd.run(main)
