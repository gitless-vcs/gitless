#!/usr/bin/python

"""gl-branch - Create, edit, delete or switch branches.

Implements the gl-branch command, part of the Gitless suite.
"""

import argparse

import branch_lib


def main():
  parser = argparse.ArgumentParser(
      description="Create, edit, delete or switch branches.")
  parser.add_argument(
      'branch', nargs='?',
      help='Switch to branch (will be created if it doesn\'t exist yet)')
  parser.add_argument(
      '-d', '--delete', nargs='+', help='Delete branch(es)', dest='delete_b')
  parser.add_argument(
      '-l', '--list', nargs='*', help='List branch(es)', dest='list_b')
  args = parser.parse_args()
  if args.branch:
    exists, is_current, unused_tracks = branch_lib.status(args.branch)
    if exists and is_current:
      print 'You are already in branch %s' % args.branch
      return

    if not exists:
      branch_lib.create(args.branch)
      print 'Created new branch %s' % args.branch


    branch_lib.switch(args.branch)
    print 'Switched to branch %s' % args.branch
  elif args.delete_b:
    print 'Delete'
  else:
    _list()


def _list():
  for name, is_current, tracks in branch_lib.status_all():
    print '%s %s %s' % (
        '*' if is_current else ' ', name,
        ('(tracks %s)' % tracks) if tracks else '')

  print ''
  print '* = current branch'


if __name__ == '__main__':
  main()
