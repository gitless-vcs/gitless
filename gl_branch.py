#!/usr/bin/python

"""gl-branch - Create, edit, delete or switch branches.

Implements the gl-branch command, part of the Gitless suite.
"""

import argparse

import cmd
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
    _delete(args.delete_b)
  else:
    _list()


def _list():
  for name, is_current, tracks in branch_lib.status_all():
    print '%s %s %s' % (
        '*' if is_current else ' ', name,
        ('(tracks %s)' % tracks) if tracks else '')

  print ''
  print '* = current branch'


def _delete(delete_b):
  for b in delete_b:
    exists, is_current, unused_tracks = branch_lib.status(b)
    if not exists:
      print 'Can\'t remove inexistent branch %s' % b
    elif exists and is_current:
      print 'Can\'t remove current branch %s' % b
    elif not _conf_dialog('Branch %s will be removed' % b):
      print 'Operation aborted'
    else:
      branch_lib.delete(b)
      print 'Branch %s removed successfully' % b


def _conf_dialog(msg):
  user_input = raw_input('%s. Do you wish to continue? (y/N) ' % msg)
  return user_input and user_input[0] == 'y'


if __name__ == '__main__':
  cmd.run(main)
