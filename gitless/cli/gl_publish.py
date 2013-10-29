# Gitless - a version control system built on top of Git.
# Copyright (c) 2013  Santiago Perez De Rosso.
# Licensed under GNU GPL, version 2.

"""gl publish - Publish commits upstream."""


from gitless.core import sync as sync_lib

import pprint


def parser(subparsers):
  """Adds the publish parser to the given subparsers object."""
  push_parser = subparsers.add_parser(
      'publish', help='publish commits upstream')
  push_parser.set_defaults(func=main)


def main(unused_args):
  ret, out = sync_lib.publish()
  success = True

  if ret == sync_lib.SUCCESS:
    print out
  elif ret == sync_lib.UPSTREAM_NOT_SET:
    pprint.err('Current branch has no upstream set')
    pprint.err_exp(
        'to set an upstream branch do gl branch --set-upstream '
        'remote/remote_branch')
    success = False
  elif ret == sync_lib.NOTHING_TO_PUSH:
    pprint.err('No commits to publish')
    success = False
  elif ret == sync_lib.PUSH_FAIL:
    pprint.err(
        'Publish failed, there are conflicting changes you need to converge')
    pprint.err_exp('use gl rebase or gl merge to converge the upstream changes')
    success = False
  else:
    raise Exception('Unrecognized ret code %s' % ret)

  return success
