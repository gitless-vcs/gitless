# Gitless - a version control system built on top of Git.
# Copyright (c) 2013  Santiago Perez De Rosso.
# Licensed under GNU GPL, version 2.

"""gl branch - Create, edit, delete or switch branches."""


import branch_lib
import sync_lib

import cmd
import pprint


def parser(subparsers):
  """Adds the branch parser to the given subparsers object."""
  branch_parser = subparsers.add_parser(
      'branch', help='create, edit, delete or switch branches')
  branch_parser.add_argument(
      'branch', nargs='?',
      help='switch to branch (will be created if it doesn\'t exist yet)')
  branch_parser.add_argument(
      '-d', '--delete', nargs='+', help='delete branch(es)', dest='delete_b')
  branch_parser.add_argument(
      '-su', '--set-upstream', help='set the upstream branch',
      dest='upstream_b')
  branch_parser.set_defaults(func=main)


def main(args):
  cmd.check_gl_dir()

  if args.branch:
    exists, is_current, unused_tracks = branch_lib.status(args.branch)
    if exists and is_current:
      pprint.err(
          'You are already in branch %s. No need to switch.' % args.branch)
      pprint.err_exp('to list existing branches do gl branch')
      return cmd.ERRORS_FOUND

    if sync_lib.rebase_in_progress():
      pprint.err(
          'You can\'t switch branches when a rebase is in progress (yet '
          '-- this will be implemented in the future)')
      return cmd.ERRORS_FOUND

    if sync_lib.merge_in_progress():
      pprint.err(
          'You can\'t switch branches when merge is in progress (yet '
          '-- this will be implemented in the future)')
      return cmd.ERRORS_FOUND

    if not exists:
      ret = branch_lib.create(args.branch)
      if ret is branch_lib.INVALID_NAME:
        pprint.err('Invalid branch name')
        return cmd.ERRORS_FOUND
      elif ret is branch_lib.SUCCESS:
        pprint.msg('Created new branch %s' % args.branch)
      else:
        raise Exception('Unrecognized ret code %s' % ret)

    branch_lib.switch(args.branch)
    pprint.msg('Switched to branch %s' % args.branch)
  elif args.delete_b:
    if not _delete(args.delete_b):
      return cmd.ERRORS_FOUND
  elif args.upstream_b:
    return _do_set_upstream(args.upstream_b)
  else:
    _list()

  return cmd.SUCCESS


def _list():
  pprint.msg('Existing branches:')
  pprint.exp('use gl branch <b> to create or switch to branch b')
  pprint.exp('use gl branch -d <b> to delete branch b')
  pprint.exp(
      'use gl branch -su <upstream> to set an upstream for the current branch')
  pprint.exp('* = current branch')
  pprint.blank()
  for name, is_current, upstream, upstream_in_remote in branch_lib.status_all():
    current_str = '*' if is_current else ' '
    upstream_str = ''
    if upstream:
      np_str = ' --not present in remote yet' if not upstream_in_remote else ''
      upstream_str = '(upstream is %s%s)' % (upstream, np_str)
    pprint.item('%s %s %s' % (current_str, name, upstream_str))


def _delete(delete_b):
  errors_found = False

  for b in delete_b:
    exists, is_current, unused_tracks = branch_lib.status(b)
    if not exists:
      pprint.err('Can\'t remove non-existent branch %s' % b)
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


def _do_set_upstream(upstream):
  if '/' not in upstream:
    pprint.err(
        'Invalid upstream branch. It must be in the format remote/branch')
    return True
  upstream_remote, upstream_branch = upstream.split('/')

  ret = branch_lib.set_upstream(upstream_remote, upstream_branch)
  errors_found = False

  if ret is branch_lib.REMOTE_NOT_FOUND:
    pprint.err('Remote %s not found' % upstream_remote)
    pprint.err_exp('do gl remote show to list all available remotes')
    pprint.err_exp(
        'to add %s as a new remote do gl remote add %s remote_url' % (
            upstream_remote, upstream_remote))
    errors_found = True
  elif ret is branch_lib.SUCCESS:
    pprint.msg('Current branch %s set to track %s/%s' % (
        branch_lib.current(), upstream_remote, upstream_branch))

  return errors_found
