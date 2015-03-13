# -*- coding: utf-8 -*-
# Gitless - a version control system built on top of Git.
# Licensed under GNU GPL v2.

"""gl branch - List, create, edit or delete branches."""


from clint.textui import colored

from gitless import core

from . import pprint
from . import helpers


def parser(subparsers):
  """Adds the branch parser to the given subparsers object."""
  branch_parser = subparsers.add_parser(
      'branch', help='list, create, edit or delete branches')
  branch_parser.add_argument(
      '-c', '--create', nargs='+', help='create branch(es)', dest='create_b')
  branch_parser.add_argument(
      '-dp', '--divergent-point',
      help='the commit from where to \'branch out\' (only relevant if a new '
      'branch is created; defaults to HEAD)', default='HEAD',
      dest='dp')
  branch_parser.add_argument(
      '-d', '--delete', nargs='+', help='delete branch(es)', dest='delete_b')
  branch_parser.add_argument(
      '-su', '--set-upstream',
      help='set the upstream branch of the current branch',
      dest='upstream_b')
  branch_parser.add_argument(
      '-uu', '--unset-upstream',
      help='unset the upstream branch of the current branch',
      action='store_true')
  branch_parser.set_defaults(func=main)


def main(args, repo):
  ret = True
  if args.create_b:
    ret = _do_create(args.create_b, args.dp, repo)
  elif args.delete_b:
    ret = _do_delete(args.delete_b, repo)
  elif args.upstream_b:
    ret = _do_set_upstream(args.upstream_b, repo)
  elif args.unset_upstream:
    ret = _do_unset_upstream(repo)
  else:
    _do_list(repo)

  return ret


def _do_list(repo):
  pprint.msg('List of branches:')
  pprint.exp('do gl branch -c <b> to create branch b')
  pprint.exp('do gl branch -d <b> to delete branch b')
  pprint.exp(
      'do gl branch -su <upstream> to set an upstream for the current branch')
  pprint.exp('* = current branch')
  pprint.blank()

  for b in (repo.lookup_branch(n) for n in repo.listall_branches()):
    current_str = '*' if b.is_current else ' '
    upstream_str = ''
    try:
      upstream_str = '(upstream is {0})'.format(b.upstream_name)
    except KeyError:
      pass
    color = colored.green if b.is_current else colored.yellow
    pprint.item(
        '{0} {1} {2}'.format(current_str, color(b.branch_name), upstream_str))


def _do_create(create_b, dp, repo):
  errors_found = False

  try:
    target = repo.revparse_single(dp)
  except KeyError:
    raise ValueError('Invalid divergent point "{0}"'.format(dp))

  for b_name in create_b:
    try:
      repo.create_branch(b_name, target)
      pprint.msg('Created new branch "{0}"'.format(b_name))
    except ValueError as e:
      pprint.err(e)
      errors_found = True

  return not errors_found


def _do_delete(delete_b, repo):
  errors_found = False

  for b_name in delete_b:
    b = repo.lookup_branch(b_name)
    if not b:
      pprint.err('Branch "{0}" doesn\'t exist'.format(b_name))
      pprint.err_exp('do gl branch to list existing branches')
      errors_found = True
      continue

    if not pprint.conf_dialog('Branch {0} will be removed'.format(b_name)):
      pprint.msg('Aborted: removal of branch {0}'.format(b_name))
      continue

    try:
      b.delete()
      pprint.msg('Branch {0} removed successfully'.format(b_name))
    except core.BranchIsCurrentError as e:
      pprint.err(e)
      pprint.err_exp(
          'do gl branch <b> to create or switch to another branch b and then '
          'gl branch -d {0} to remove branch {0}'.format(b_name))
      errors_found = True

  return not errors_found


def _do_set_upstream(upstream, repo):
  repo.current_branch.upstream = helpers.get_branch(upstream, repo)
  pprint.msg('Current branch {0} set to track {1}'.format(
      colored.green(repo.current_branch.branch_name), upstream))

  return True


def _do_unset_upstream(repo):
  repo.current_branch.upstream = None
  pprint.msg('Upstream unset for current branch')
  return True
