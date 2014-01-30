# Gitless - a version control system built on top of Git.
# Copyright (c) 2013  Santiago Perez De Rosso.
# Licensed under GNU GPL, version 2.

"""gl remote - {Add, remove, get info of} remotes."""


from gitless.core import remote as remote_lib

from . import pprint


def parser(subparsers):
  """Adds the remote parser to the given subparsers object."""
  remote_parser = subparsers.add_parser(
      'remote', help='list, create or delete remotes')

  remote_parser.add_argument(
      'remote_name', nargs='?', help='the name of the remote')
  remote_parser.add_argument(
      'remote_url', nargs='?',
      help='the url of the remote. Only relevant when adding a new remote')
  remote_parser.add_argument(
      '-d', '--delete', nargs='+', help='delete remote(es)', dest='delete_r')
  # TODO(sperezde): do this.
#  remote_parser.add_argument(
#      '-v', '--verbose',
#      help='be verbose, will output more info when listing remotes',
#      action='store_true')

  remote_parser.set_defaults(func=main)


def main(args):
  if args.remote_name:
    return _do_add(args)
  elif args.delete_r:
    return _do_delete(args.delete_r)
  else:
    _do_list()
    return True


def _do_add(args):
  rn = args.remote_name
  ru = args.remote_url
  ret = remote_lib.add(rn, ru)
  success = True

  if ret == remote_lib.REMOTE_ALREADY_SET:
    pprint.err('There\'s already a remote set with that name')
    pprint.err_exp('to list existing remotes do gl remote')
    pprint.err_exp(
        'if you want to change the url for remote %s do gl remote -d %s, and '
        'then gl remote %s new_url' % (rn, rn, rn))
    success = False
  elif ret == remote_lib.REMOTE_UNREACHABLE:
    pprint.err('Couldn\'t reach {0} to create {1}'.format(ru, rn))
    pprint.err_exp('make sure that you are connected to the internet')
    pprint.err_exp(
        'make sure that you have permissions to access the remote')
    success = False
  elif ret == remote_lib.INVALID_NAME:
    pprint.err(
        'Invalid remote name {0}, remote names can\'t have \'/\''.format(ru))
    success = False
  elif ret == remote_lib.SUCCESS:
    pprint.msg('Remote {0} mapping to {1} created successfully'.format(rn, ru))
    pprint.exp('to list existing remotes do gl remote')
    pprint.exp('to remove {0} do gl remote -d {1}'.format(rn, rn))
  else:
    raise Exception('Unrecognized ret code %s' % ret)

  return success


def _do_list():
  pprint.msg('List of remotes:')
  pprint.exp('do gl remote <r> <r_url> to add a new remote r mapping to r_url')
  pprint.exp('do gl remote -d <r> to delete remote r')
  remotes = remote_lib.info_all()
  pprint.blank()
  if not remotes:
    pprint.item('There are no remotes to list')
  else:
    for rn in remotes:
      mapping = ' (maps to {0})'.format(rn.upstream)
      if rn.downstream != rn.upstream:
        mapping = ' (maps to {0} downstream, {1} upstream)'.format(
            rn.downstream, rn.upstream)
      pprint.item(rn.name, opt_text=mapping)
  return True


#def _print_remote(rn, verbose):
#  success = True
#  pprint.item(rn)
#  if verbose:
#    ret, info = remote_lib.info(rn)
#    if ret == remote_lib.REMOTE_UNREACHABLE:
#      pprint.item_info(
#          'Couldn\'t reach remote %s to get more info abou it' % rn)
#      pprint.item_info(
#           'make sure that you are still connected to the internet')
#      pprint.item_info(
#          'make sure that you still have permissions to access the remote')
#      success = False
#    elif ret == remote_lib.SUCCESS:
#      pprint.item_info(info)
#    else:
#      raise Exception('Unrecognized ret code %s' % ret)
#  return success


def _do_delete(delete_r):
  errors_found = False

  for r in delete_r:
    ret = remote_lib.rm(r)
    if ret == remote_lib.REMOTE_NOT_FOUND:
      pprint.err('Remote %s not found' % r)
      errors_found = True
    elif ret == remote_lib.SUCCESS:
      pprint.msg('Remote %s removed successfully' % r)
    else:
      raise Exception('Unrecognized ret code %s' % ret)

  return not errors_found
