# -*- coding: utf-8 -*-
# Gitless - a version control system built on top of Git.
# Licensed under GNU GPL v2.

"""gl branch - List, create, edit or delete branches."""


from __future__ import unicode_literals

from clint.textui import colored

from gitless import core

from . import helpers, pprint


def parser(subparsers, _):
  """Adds the branch parser to the given subparsers object."""
  desc = 'list, create, delete, or edit branches'
  branch_parser = subparsers.add_parser(
      'branch', help=desc, description=desc.capitalize())

  list_group = branch_parser.add_argument_group('list branches')
  list_group.add_argument(
      '-r', '--remote',
      help='list remote branches in addition to local branches',
      action='store_true')
  list_group.add_argument(
      '-v', '--verbose', help='be verbose, will output the head of each branch',
      action='store_true')

  create_group = branch_parser.add_argument_group('create branches')
  create_group.add_argument(
      '-c', '--create', nargs='+', help='create branch(es)', dest='create_b',
      metavar='branch')
  create_group.add_argument(
      '-dp', '--divergent-point',
      help='the commit from where to \'branch out\' (only relevant if a new '
      'branch is created; defaults to HEAD)', dest='dp')

  delete_group = branch_parser.add_argument_group('delete branches')
  delete_group.add_argument(
      '-d', '--delete', nargs='+', help='delete branch(es)', dest='delete_b',
      metavar='branch')

  edit_group = branch_parser.add_argument_group('edit the current branch')
  edit_group.add_argument(
      '-sh', '--set-head', help='set the head of the current branch',
      dest='new_head', metavar='commit_id')
  edit_group.add_argument(
      '-su', '--set-upstream',
      help='set the upstream branch of the current branch',
      dest='upstream_b', metavar='branch')
  edit_group.add_argument(
      '-uu', '--unset-upstream',
      help='unset the upstream branch of the current branch',
      action='store_true')

  branch_parser.set_defaults(func=main)


def main(args, repo):
  is_list = bool(args.verbose or args.remote)
  is_create = bool(args.create_b or args.dp)
  is_delete = bool(args.delete_b)
  is_edit = bool(args.new_head or args.upstream_b or args.unset_upstream)

  if is_list + is_create + is_delete + is_edit > 1:
    pprint.err('Invalid flag combination')
    pprint.err_exp(
        'Can only do one of list, create, delete, or edit branches at a time')
    return False

  ret = True
  if args.create_b:
    ret = _do_create(args.create_b, args.dp or 'HEAD', repo)
  elif args.delete_b:
    ret = _do_delete(args.delete_b, repo)
  elif args.upstream_b:
    ret = _do_set_upstream(args.upstream_b, repo)
  elif args.unset_upstream:
    ret = _do_unset_upstream(repo)
  elif args.new_head:
    ret = _do_set_head(args.new_head, repo)
  else:
    _do_list(repo, args.remote, v=args.verbose)

  return ret


def _do_list(repo, list_remote, v=False):
  pprint.msg('List of branches:')
  pprint.exp('do gl branch -c b to create branch b')
  pprint.exp('do gl branch -d b to delete branch b')
  pprint.exp('do gl switch b to switch to branch b')
  pprint.exp('* = current branch')
  pprint.blank()


  for b in (repo.lookup_branch(n) for n in sorted(repo.listall_branches())):
    current_str = '*' if b.is_current else ' '
    upstream_str = '(upstream is {0})'.format(b.upstream) if b.upstream else ''
    color = colored.green if b.is_current else colored.yellow
    pprint.item(
        '{0} {1} {2}'.format(current_str, color(b.branch_name), upstream_str))
    if v:
      pprint.item('    ➜ head is {0}'.format(pprint.commit_str(b.head)))

  if list_remote:
    for r in sorted(repo.remotes, key=lambda r: r.name):
      for b in (r.lookup_branch(n) for n in sorted(r.listall_branches())):
        pprint.item('  {0}'.format(colored.yellow(str(b))))
        if v:
          pprint.item('    ➜ head is {0}'.format(pprint.commit_str(b.head)))


def _do_create(create_b, dp, repo):
  errors_found = False

  try:
    target = repo.revparse_single(dp)
  except KeyError:
    raise ValueError('Invalid divergent point {0}'.format(dp))

  for b_name in create_b:
    r = repo
    remote_str = ''
    if '/' in b_name:  # might want to create a remote branch
      maybe_remote, maybe_remote_branch = b_name.split('/', 1)
      if maybe_remote in repo.remotes:
        r = repo.remotes[maybe_remote]
        b_name = maybe_remote_branch
        conf_msg = 'Branch {0} will be created in remote repository {1}'.format(
            b_name, maybe_remote)
        if not pprint.conf_dialog(conf_msg):
          pprint.msg(
              'Aborted: creation of branch {0} in remote repository {1}'.format(
                  b_name, maybe_remote))
          continue
        remote_str = ' in remote repository {0}'.format(maybe_remote)
    try:
      r.create_branch(b_name, target)
      pprint.ok('Created new branch {0}{1}'.format(b_name, remote_str))
    except ValueError as e:
      pprint.err(e)
      errors_found = True

  return not errors_found


def _do_delete(delete_b, repo):
  errors_found = False

  for b_name in delete_b:
    try:
      b = helpers.get_branch(b_name, repo)

      branch_str = 'Branch {0} will be removed'.format(b.branch_name)
      remote_str = ''
      if isinstance(b, core.RemoteBranch):
        remote_str = 'from remote repository {0}'.format(b.remote_name)
      if not pprint.conf_dialog('{0} {1}'.format(branch_str, remote_str)):
        pprint.msg('Aborted: removal of branch {0}'.format(b))
        continue

      b.delete()
      pprint.ok('Branch {0} removed successfully'.format(b))
    except ValueError as e:
      pprint.err(e)
      errors_found = True
    except core.BranchIsCurrentError as e:
      pprint.err(e)
      pprint.err_exp(
          'do gl branch b to create or switch to another branch b and then '
          'gl branch -d {0} to remove branch {0}'.format(b))
      errors_found = True

  return not errors_found


def _do_set_upstream(upstream, repo):
  curr_b = repo.current_branch
  curr_b.upstream = helpers.get_branch(upstream, repo)
  pprint.ok('Current branch {0} set to track {1}'.format(curr_b, upstream))
  return True


def _do_unset_upstream(repo):
  curr_b = repo.current_branch
  curr_b.upstream = None
  pprint.ok('Upstream unset for current branch {0}'.format(curr_b))
  return True


def _do_set_head(commit_id, repo):
  try:
    commit = repo.revparse_single(commit_id)
  except KeyError:
    raise ValueError('Invalid head {0}'.format(commit_id))

  curr_b = repo.current_branch
  curr_b.head = commit.id
  pprint.ok(
      'Head of current branch {0} is now {1}'.format(curr_b, pprint.commit_str(commit)))
  return True
