# Gitless - a version control system built on top of Git.
# Licensed under GNU GPL v2.

"""gl branch - Create, edit, delete or switch branches."""


from clint.textui import colored

from gitless.core import branch as branch_lib
from gitless.core import sync as sync_lib

from . import pprint


def parser(subparsers):
  """Adds the branch parser to the given subparsers object."""
  branch_parser = subparsers.add_parser(
      'branch', help='list, create, edit, delete or switch branches')
  branch_parser.add_argument(
      'branch', nargs='?',
      help='switch to branch (will be created if it doesn\'t exist yet)')
  branch_parser.add_argument(
      'divergent_point', nargs='?',
      help='the commit from where to \'branch out\' (only relevant if a new '
      'branch is created; defaults to HEAD)', default='HEAD')
  branch_parser.add_argument(
      '-d', '--delete', nargs='+', help='delete branch(es)', dest='delete_b')
  branch_parser.add_argument(
      '-su', '--set-upstream', help='set the upstream branch',
      dest='upstream_b')
  branch_parser.add_argument(
      '-uu', '--unset-upstream', help='unset the upstream branch',
      action='store_true')
  branch_parser.set_defaults(func=main)


def main(args):
  ret = True
  if args.branch:
    b_st = branch_lib.status(args.branch)
    if b_st and b_st.is_current:
      pprint.err(
          'You are already in branch {0}. No need to switch.'.format(
              colored.green(args.branch)))
      pprint.err_exp('to list existing branches do gl branch')
      return False

    if sync_lib.rebase_in_progress():
      pprint.err(
          'You can\'t switch branches when a rebase is in progress (yet '
          '-- this will be implemented in the future)')
      return False
    elif sync_lib.merge_in_progress():
      pprint.err(
          'You can\'t switch branches when merge is in progress (yet '
          '-- this will be implemented in the future)')
      return False

    if not b_st and not _do_create(args.branch, args.divergent_point):
      return False

    branch_lib.switch(args.branch)
    pprint.msg('Switched to branch {0}'.format(colored.green(args.branch)))
  elif args.delete_b:
    ret = _do_delete(args.delete_b)
  elif args.upstream_b:
    ret = _do_set_upstream(args.upstream_b)
  elif args.unset_upstream:
    ret = _do_unset_upstream()
  else:
    _do_list()

  return ret


def _do_create(branch_name, divergent_point):
  errors_found = False

  ret = branch_lib.create(branch_name, dp=divergent_point)
  if ret == branch_lib.INVALID_NAME:
    pprint.err('Invalid branch name')
    errors_found = True
  elif ret == branch_lib.INVALID_DP:
    pprint.msg('Invalid divergent point {0}'.format(divergent_point))
    errors_found = True
  elif ret == branch_lib.SUCCESS:
    pprint.msg('Created new branch {0}'.format(branch_name))
  else:
    raise Exception('Unrecognized ret code {0}'.format(ret))
  return not errors_found


def _do_list():
  pprint.msg('List of branches:')
  pprint.exp('do gl branch <b> to create or switch to branch b')
  pprint.exp('do gl branch -d <b> to delete branch b')
  pprint.exp(
      'do gl branch -su <upstream> to set an upstream for the current branch')
  pprint.exp('* = current branch')
  pprint.blank()
  for name, is_current, upstream, upstream_exists in branch_lib.status_all():
    current_str = '*' if is_current else ' '
    upstream_str = ''
    if upstream:
      np_str = ' --not present in remote yet' if not upstream_exists else ''
      upstream_str = '(upstream is {0}{1})'.format(upstream, np_str)
    color = colored.green if is_current else colored.yellow
    pprint.item('{0} {1} {2}'.format(current_str, color(name), upstream_str))


def _do_delete(delete_b):
  errors_found = False

  for b in delete_b:
    b_st = branch_lib.status(b)
    cb = colored.green(b)
    if not b_st:
      pprint.err('Can\'t remove non-existent branch {0}'.format(cb))
      pprint.err_exp('do gl branch to list existing branches')
      errors_found = True
    elif b_st and b_st.is_current:
      pprint.err('Can\'t remove current branch {0}'.format(cb))
      pprint.err_exp(
          'do gl branch <b> to create or switch to another branch b and then '
          'gl branch -d {0} to remove branch {0}'.format(cb))
      errors_found = True
    elif not pprint.conf_dialog('Branch {0} will be removed'.format(cb)):
      pprint.msg('Aborted: removal of branch {0}'.format(cb))
    else:
      branch_lib.delete(b)
      pprint.msg('Branch {0} removed successfully'.format(cb))

  return not errors_found


def _do_set_upstream(upstream):
  if '/' not in upstream:
    pprint.err(
        'Invalid upstream branch. It must be in the format remote/branch')
    return True

  ret = branch_lib.set_upstream(upstream)

  errors_found = False
  upstream_remote, upstream_branch = upstream.split('/')
  if ret is branch_lib.REMOTE_NOT_FOUND:
    pprint.err('Remote {0} not found'.format(upstream_remote))
    pprint.err_exp('do gl remote to list all existing remotes')
    pprint.err_exp(
        'do gl remote {0} <r_url> to add a new remote {0} mapping to '
        'r_url'.format(upstream_remote))
    errors_found = True
  elif ret is branch_lib.SUCCESS:
    pprint.msg(
        'Current branch {0} set to track {1}/{2}'.format(
            colored.green(branch_lib.current()), upstream_remote,
            upstream_branch))

  return not errors_found


def _do_unset_upstream():
  ret = branch_lib.unset_upstream()

  errors_found = False
  if ret is branch_lib.UPSTREAM_NOT_SET:
    pprint.err('Current branch has no upstream set')
    pprint.err_exp(
        'do gl branch to list all existing branches -- if a branch has an '
        'upstream set it will be shown')
    pprint.err_exp(
      'do gl branch -su <upstream> to set an upstream for the current branch')
    errors_found = True
  elif ret is branch_lib.SUCCESS:
    pprint.msg('Upstream unset for current branch')

  return not errors_found
