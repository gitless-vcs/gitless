#!/usr/bin/python

"""gl-merge - Merge the divergent changes of one branch onto another.

Implements the gl-merge command, part of the Gitless suite.
"""

import argparse
import sys

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
    parser.error('No src branch specified')

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
