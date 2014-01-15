# Gitless - a version control system built on top of Git.
# Copyright (c) 2013  Santiago Perez De Rosso.
# Licensed under GNU GPL, version 2.

"""gl remote - Set the remote for the repo, get info about it."""


from gitless.core import remote as remote_lib

import pprint


def parser(subparsers):
  """Adds the remote parser to the given subparsers object."""
  remote_parser = subparsers.add_parser(
      'remote', help='add/rm remotes, get info about them')

  remote_subparsers = remote_parser.add_subparsers()

  add_parser = remote_subparsers.add_parser('add', help='add remote')
  add_parser.add_argument('remote_name', help='the name of the remote')
  add_parser.add_argument('remote_url', help='the url of the remote')
  add_parser.set_defaults(func=_do_add)

  rm_parser = remote_subparsers.add_parser('rm', help='remove remote')
  rm_parser.add_argument('remote_name', help='the name of the remote to remove')
  rm_parser.set_defaults(func=_do_rm)

  show_parser = remote_subparsers.add_parser(
      'show', help='show info about remote')
  show_parser.add_argument(
      'remote_name', nargs='?',
      help='display information about the remote name given. If none is given, '
      'lists all remotes')
  show_parser.set_defaults(func=_do_show)


def _do_add(args):
  rn = args.remote_name
  ru = args.remote_url
  ret, info = remote_lib.add(rn, ru)
  success = True

  if ret is remote_lib.REMOTE_ALREADY_SET:
    pprint.err('There\'s already a remote set with that name')
    pprint.err_exp(
        'to get information about %s do gl remote show %s' % (rn, rn))
    pprint.err_exp(
        'if you want to change the url for remote %s do gl remote rm %s, and '
        'then gl remote add %s new_url' % (rn, rn, rn))
    success = False
  elif ret is remote_lib.SUCCESS:
    pprint.msg('Remote added successfully')
    pprint.exp(
        'to get information about %s do gl remote show %s' % (rn, rn))
    pprint.exp('to remove %s do gl remote rm %s' % (rn, rn))
    # TODO(sperezde): Print the info was we parse it.
    #pprint.blank()
    #pprint.msg('Info about remote:')
    #pprint.blank()
    #pprint.item(info)
  else:
    raise Exception('Unrecognized ret code %s' % ret)

  return success


def _do_show(args):
  rn = args.remote_name

  success = True

  if rn:
    ret, info = remote_lib.info(rn)
    if ret is remote_lib.REMOTE_NOT_FOUND:
      pprint.err('Remote %s not found' % rn)
      pprint.err_exp('to list all existing remotes do gl remote show')
      success = False
    elif ret is remote_lib.REMOTE_UNREACHABLE:
      pprint.err('Couldn\'t reach remote %s' % rn)
      pprint.err_exp('make sure that you are still connected to the internet')
      pprint.err_exp(
          'make sure that you still have permissions to access the remote')
      success = False
    elif ret is remote_lib.SUCCESS:
      pprint.msg(info)
    else:
      raise Exception('Unrecognized ret code %s' % ret)
  else:
    pprint.msg('List of remotes:')
    pprint.exp('to remove a remote do gl remote rm remote_name')
    pprint.exp('to add a new remote do gl remote add remote_name remote_url')
    pprint.exp(
        'to get more information about a particular remote do gl remote show '
        'remote_name')
    remotes = remote_lib.list()
    pprint.blank()
    if not remotes:
      pprint.item('There are no remotes to list')
    else:
      for rn in remote_lib.list():
        pprint.item(rn)

  return success


def _do_rm(args):
  rn = args.remote_name
  ret = remote_lib.rm(rn)
  success = True

  if ret is remote_lib.REMOTE_NOT_FOUND:
    pprint.err('Remote %s not found' % rn)
    pprint.err_exp('to list all existing remotes do gl remote show')
    success = False
  elif ret is remote_lib.SUCCESS:
    pprint.msg('Remote %s removed' % rn)
  else:
    raise Exception('Unrecognized ret code %s' % ret)

  return success
