#!/usr/bin/python

"""gl-push - Push changes upstream.

Implements the gl-push command, part of the Gitless suite.
"""

import argparse

import cmd
import pprint
import sync_lib


def main():
  ret, out = sync_lib.push()
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
    pprint.err('Nothing to push')
    errors_found = True
  elif ret is sync_lib.PUSH_FAIL:
    pprint.err(
        'Push failed, there are conflicting changes you need to converge')
    pprint.err_exp('use gl rebase or gl merge to converge the upstream changes')
    errors_found = True
  else:
    raise Exception('Unrecognized ret code %s' % ret)

  return cmd.ERRORS_FOUND if errors_found else cmd.SUCCESS


if __name__ == '__main__':
  cmd.run(main)
