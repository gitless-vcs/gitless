#!/usr/bin/python

"""gl - Main Gitless's command. Dispatcher to the other cmds."""

import argparse
import sys

import cmd
import gl_track
import gl_untrack
import gl_status
import gl_diff
import gl_commit
import gl_branch
import gl_checkout
import gl_rm
import gl_merge
import gl_resolve
import gl_rebase
import gl_remote
import gl_push
import gl_init
import gl_history
import pprint


def main():
  cmds = {
      'track': gl_track, 'untrack': gl_untrack, 'status': gl_status,
      'diff': gl_diff, 'commit': gl_commit, 'branch': gl_branch,
      'checkout': gl_checkout, 'rm': gl_rm, 'merge': gl_merge,
      'resolve': gl_resolve, 'rebase': gl_rebase, 'remote': gl_remote,
      'push': gl_push, 'init': gl_init, 'history': gl_history}

  if len(sys.argv) <= 1:
    # No action was provided.
    pprint.err('No action was provided')
    pprint.err_exp(
        'action must be one of the following: %s' % ', '.join(cmds.keys()))
    return cmd.ERRORS_FOUND

  action = sys.argv[1]
  if action not in cmds:
    pprint.err('Unrecognized action %s' % action)
    pprint.err_exp(
        'action must be one of the following: %s' % ', '.join(cmds.keys()))
    return cmd.ERRORS_FOUND

  sys.argv.pop(1)
  sys.argv[0] = '/usr/bin/gl-%s' % action

  return cmd.run(cmds[action].main, is_init=(action == 'init'))


if __name__ == '__main__':
  # Potentially init.
  cmd.run(main, is_init=True)
