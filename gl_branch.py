#!/usr/bin/python

"""gl-branch - Create, edit, delete or switch branches.

Implements the gl-branch command, part of the Gitless suite.
"""

import argparse

import cmd
import branch_lib
import pprint


def main():
  parser = argparse.ArgumentParser(
      description="Create, edit, delete or switch branches.")
  parser.add_argument(
      'branch', nargs='?',
      help='Switch to branch (will be created if it doesn\'t exist yet)')
  parser.add_argument(
      '-d', '--delete', nargs='+', help='Delete branch(es)', dest='delete_b')
  args = parser.parse_args()


  if args.branch:
    exists, is_current, unused_tracks = branch_lib.status(args.branch)
    if exists and is_current:
      pprint.err(
          'You are already in branch %s. No need to switch.' % args.branch)
      pprint.err_exp('to list existing branches do gl branch')
      return cmd.ERRORS_FOUND

    if not exists:
      branch_lib.create(args.branch)
      pprint.msg('Created new branch %s' % args.branch)


    branch_lib.switch(args.branch)
    pprint.msg('Switched to branch %s' % args.branch)
  elif args.delete_b:
    if not _delete(args.delete_b):
      return cmd.ERRORS_FOUND
  else:
    _list()

  return cmd.SUCCESS


def _list():
  pprint.msg('Existing branches:')
  pprint.exp('use gl branch <b> to create or switch to branch b')
  pprint.exp('use gl branch -d <b> to delete branch b')
  pprint.exp('* = current branch')
  pprint.blank()
  for name, is_current, tracks in branch_lib.status_all():
    pprint.item(
        '%s %s %s' % (
        '*' if is_current else ' ', name,
        ('(tracks %s)' % tracks) if tracks else ''))


def _delete(delete_b):
  errors_found = False

  for b in delete_b:
    exists, is_current, unused_tracks = branch_lib.status(b)
    if not exists:
      pprint.err('Can\'t remove inexistent branch %s' % b)
      pprint.err_exp('to list existing branches do gl branch')
      errors_found = True
    elif exists and is_current:
      pprint.err('Can\'t remove current branch %s' % b)
      pprint.err_exp(
          'use gl branch <b> to create or switch to another branch b and then '
          'gl branch -d %s to remove branch %s' % (b, b))
      errors_found = True
    elif not pprint.conf_dialog('Branch %s will be removed' % b):
      pprint.msg('Aborted: removal of branch %s' % b)
    else:
      branch_lib.delete(b)
      pprint.msg('Branch %s removed successfully' % b)

  return not errors_found


if __name__ == '__main__':
  cmd.run(main)
