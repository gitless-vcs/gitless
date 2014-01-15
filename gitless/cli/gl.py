# Gitless - a version control system built on top of Git.
# Copyright (c) 2013  Santiago Perez De Rosso.
# Licensed under GNU GPL, version 2.

"""gl - Main Gitless's command. Dispatcher to the other cmds."""


import argparse
import pkg_resources
import traceback

from gitless.core import repo as repo_lib

import gl_track
import gl_untrack
import gl_status
import gl_diff
import gl_commit
import gl_branch
import gl_checkout
import gl_merge
import gl_rebase
import gl_remote
import gl_resolve
import gl_publish
import gl_init
import gl_history
import pprint


SUCCESS = 0
ERRORS_FOUND = 1
# 2 is used by argparse to indicate cmd syntax errors.
INTERNAL_ERROR = 3
NOT_IN_GL_REPO = 4

GL_VERSION = 'GL Version: ' + pkg_resources.require('gitless')[0].version


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--version', action='version', version=GL_VERSION)
  subparsers = parser.add_subparsers(dest='subcmd_name')

  sub_cmds = {
      gl_track, gl_untrack, gl_status, gl_diff, gl_commit, gl_branch,
      gl_checkout, gl_merge, gl_resolve, gl_rebase, gl_remote, gl_publish,
      gl_init, gl_history}
  for sub_cmd in sub_cmds:
    sub_cmd.parser(subparsers)

  args = parser.parse_args()
  if args.subcmd_name != 'init' and not repo_lib.gl_dir():
    pprint.err(
        'You are not in a Gitless repository. To make this directory a '
        'repository do gl init. For cloning existing repositories do gl init '
        'repo.')
    return NOT_IN_GL_REPO

  try:
    return SUCCESS if args.func(args) else ERRORS_FOUND
  except KeyboardInterrupt:
    # The user pressed Crl-c.
    print '\n'
    pprint.msg('Keyboard interrupt detected, operation aborted')
    return SUCCESS
  except:
    pprint.err(
        'Oops...something went wrong (recall that Gitless is in beta). If you '
        'want to help, report the bug at '
        'http://people.csail.mit.edu/sperezde/gitless/community.html and '
        'include the following in the email:\n\n%s\n\n%s' %
        (GL_VERSION, traceback.format_exc()))
    return INTERNAL_ERROR
