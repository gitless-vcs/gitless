# Gitless - a version control system built on top of Git.
# Licensed under GNU GPL v2.

"""gl remote - List, create, edit or delete remotes."""


from gitless.core import core

from . import pprint


def parser(subparsers):
  """Adds the remote parser to the given subparsers object."""
  remote_parser = subparsers.add_parser(
      'remote', help='list, create, edit or delete remotes')
  remote_parser.add_argument(
      '-c', '--create', nargs='?', help='create remote', dest='remote_name')
  remote_parser.add_argument(
      'remote_url', nargs='?',
      help='the url of the remote (only relevant if a new remote is created)')
  remote_parser.add_argument(
      '-d', '--delete', nargs='+', help='delete remote(es)', dest='delete_r')
  remote_parser.set_defaults(func=main)


def main(args):
  ret = True
  repo = core.Repository()
  remotes = repo.remotes
  if args.remote_name:
    if not args.remote_url:
      raise ValueError('Missing url')
    ret = _do_create(args.remote_name, args.remote_url, remotes)
  elif args.delete_r:
    ret = _do_delete(args.delete_r, remotes)
  else:
    ret = _do_list(remotes)

  return ret


def _do_list(remotes):
  pprint.msg('List of remotes:')
  pprint.exp(
      'do gl remote -c <r> <r_url> to add a new remote r mapping to r_url')
  pprint.exp('do gl remote -d <r> to delete remote r')
  pprint.blank()

  if not len(remotes):
    pprint.item('There are no remotes to list')
  else:
    for r in remotes:
      pprint.item(r.name, opt_text=' (maps to {0})'.format(r.url))
  return True


def _do_create(rn, ru, remotes):
  remotes.create(rn, ru)
  pprint.msg('Remote {0} mapping to {1} created successfully'.format(rn, ru))
  pprint.exp('to list existing remotes do gl remote')
  pprint.exp('to remove {0} do gl remote -d {1}'.format(rn, rn))
  return True


def _do_delete(delete_r, remotes):
  errors_found = False

  for r in delete_r:
    try:
      remotes.delete(r)
      pprint.msg('Remote {0} removed successfully'.format(r))
    except KeyError:
      pprint.err('Remote \'{0}\' doesn\'t exist'.format(r))
      errors_found = True
  return not errors_found
