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
      pprint.msg('No merge in progress, nothing to abort')
      pprint.exp(
          'To merge divergent changes of branch b onto the current branch do gl'
          ' merge <b>')
    else:
     pprint.msg('Merge aborted')
    return

  if not args.src:
    parser.error('No src branch specified')

  ret, out = sync_lib.merge(args.src)
  if ret is sync_lib.SRC_NOT_FOUND:
    pprint.msg('Branch %s not found' % args.src, sys.stdout.write)
    pprint.exp('do gl branch to list all existing branches', sys.stdout.write)
  elif ret is sync_lib.SRC_IS_CURRENT_BRANCH:
    pprint.msg('Branch %s is the current branch' % args.src, sys.stdout.write)
    pprint.exp(
        'to merge branch %s onto another branch b, do gl branch b, and gl merge'
        ' %s from there' % (args.src, args.src), sys.stdout.write)
  elif ret is sync_lib.NOTHING_TO_MERGE:
    pprint.msg(
        'No divergent changes to merge from %s' % args.src, sys.stdout.write)
  elif ret is sync_lib.LOCAL_CHANGES_WOULD_BE_LOST:
    pprint.msg(
        'Merge was aborted because your local changes to the following files '
        'would be overwritten by merge:', sys.stdout.write)
    pprint.exp('use gl commit to commit your changes', sys.stdout.write)
    pprint.exp(
        'use gl checkout HEAD f to discard changes to tracked file f',
        sys.stdout.write)
    for fp in out:
      pprint.file(fp, '', sys.stdout.write)




if __name__ == '__main__':
  cmd.run(main)
