# Gitless - a version control system built on top of Git.
# Copyright (c) 2013  Santiago Perez De Rosso.
# Licensed under GNU GPL, version 2.

"""gl publish - Publish commits upstream."""


import sync_lib

import cmd
import pprint


def parser(subparsers):
  """Adds the publish parser to the given subparsers object."""
  push_parser = subparsers.add_parser(
      'push', help='publish commits upstream')
  push_parser.set_defaults(func=main)


def main(args):
  cmd.check_gl_dir()
  ret, out = sync_lib.publish()
  errors_found = False

  if ret is sync_lib.SUCCESS:
    print out
  elif ret is sync_lib.UPSTREAM_NOT_SET:
    pprint.err('Current branch has no upstream set')
    pprint.err_exp(
        'to set an upstream branch do gl branch --set-upstream '
        'remote/remote_branch')
    errors_found = True
  elif ret is sync_lib.NOTHING_TO_PUSH:
    pprint.err('No commits to publish')
    errors_found = True
  elif ret is sync_lib.PUSH_FAIL:
    pprint.err(
        'Publish failed, there are conflicting changes you need to converge')
    pprint.err_exp('use gl rebase or gl merge to converge the upstream changes')
    errors_found = True
  else:
    raise Exception('Unrecognized ret code %s' % ret)

  return cmd.ERRORS_FOUND if errors_found else cmd.SUCCESS
