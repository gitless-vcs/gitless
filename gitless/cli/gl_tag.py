# -*- coding: utf-8 -*-
# Gitless - a version control system built on top of Git.
# Licensed under GNU GPL v2.

"""gl tag - List, create, edit or delete tags."""


from __future__ import unicode_literals

from gitless import core

from . import helpers, pprint


def parser(subparsers, _):
  """Adds the tag parser to the given subparsers object."""
  desc = 'list, create, or delete tags'
  tag_parser = subparsers.add_parser(
      'tag', help=desc, description=desc.capitalize())

  list_group = tag_parser.add_argument_group('list tags')
  list_group.add_argument(
      '-r', '--remote',
      help='list remote tags in addition to local tags',
      action='store_true')

  create_group = tag_parser.add_argument_group('create tags')
  create_group.add_argument(
      '-c', '--create', nargs='+', help='create tag(s)', dest='create_t',
      metavar='tag')
  create_group.add_argument(
      '-ci', '--commit',
      help='the commit to tag (only relevant if a new '
      'tag is created; defaults to the HEAD commit)', dest='ci')

  delete_group = tag_parser.add_argument_group('delete tags')
  delete_group.add_argument(
      '-d', '--delete', nargs='+', help='delete tag(s)', dest='delete_t',
      metavar='tag')

  tag_parser.set_defaults(func=main)


def main(args, repo):
  is_list = bool(args.remote)
  is_create = bool(args.create_t or args.ci)
  is_delete = bool(args.delete_t)

  if is_list + is_create + is_delete > 1:
    pprint.err('Invalid flag combination')
    pprint.err_exp('Can only do one of list, create, or delete tags at a time')
    return False

  ret = True
  if args.create_t:
    ret = _do_create(args.create_t, args.ci or 'HEAD', repo)
  elif args.delete_t:
    ret = _do_delete(args.delete_t, repo)
  else:
    _do_list(repo, args.remote)

  return ret


def _do_list(repo, list_remote):
  pprint.msg('List of tags:')
  pprint.exp('do gl tag -c t to create tag t')
  pprint.exp('do gl tag -d t to delete tag t')
  pprint.blank()

  no_tags = True
  for t in (repo.lookup_tag(n) for n in sorted(repo.listall_tags())):
    pprint.item('{0} ➜ tags {1}'.format(t, pprint.commit_str(t.commit)))
    no_tags = False

  if list_remote:
    for r in sorted(repo.remotes, key=lambda r: r.name):
      for t in (r.lookup_tag(n) for n in sorted(r.listall_tags())):
        pprint.item('{0} ➜ tags {1}'.format(t, pprint.commit_str(t.commit)))
        no_tags = False

  if no_tags:
    pprint.item('There are no tags to list')


def _do_create(create_t, dp, repo):
  errors_found = False

  try:
    target = repo.revparse_single(dp)
  except KeyError:
    raise ValueError('Invalid commit {0}'.format(dp))

  for t_name in create_t:
    r = repo
    remote_str = ''
    if '/' in t_name:  # might want to create a remote tag
      maybe_remote, maybe_remote_tag = t_name.split('/', 1)
      if maybe_remote in repo.remotes:
        r = repo.remotes[maybe_remote]
        t_name = maybe_remote_tag
        conf_msg = 'Tag {0} will be created in remote repository {1}'.format(
            t_name, maybe_remote)
        if not pprint.conf_dialog(conf_msg):
          pprint.msg(
              'Aborted: creation of tag {0} in remote repository {1}'.format(
                  t_name, maybe_remote))
          continue
        remote_str = ' in remote repository {0}'.format(maybe_remote)
    try:
      r.create_tag(t_name, target)
      pprint.ok('Created new tag {0}{1}'.format(t_name, remote_str))
    except ValueError as e:
      pprint.err(e)
      errors_found = True

  return not errors_found


def _do_delete(delete_t, repo):
  errors_found = False

  for t_name in delete_t:
    try:
      t = helpers.get_tag(t_name, repo)

      tag_str = 'Tag {0} will be removed'.format(t.tag_name)
      remote_str = ''
      if isinstance(t, core.RemoteTag):
        remote_str = 'from remote repository {0}'.format(t.remote_name)
      if not pprint.conf_dialog('{0} {1}'.format(tag_str, remote_str)):
        pprint.msg('Aborted: removal of tag {0}'.format(t))
        continue

      t.delete()
      pprint.ok('Tag {0} removed successfully'.format(t))
    except ValueError as e:
      pprint.err(e)
      errors_found = True

  return not errors_found
