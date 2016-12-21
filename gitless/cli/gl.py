# -*- coding: utf-8 -*-
# Gitless - a version control system built on top of Git.
# Licensed under GNU GPL v2.

"""gl - Main Gitless's command. Dispatcher to the other cmds."""


from __future__ import unicode_literals

import sys
import argparse
import traceback
import pygit2

if sys.platform != 'win32':
  from sh import ErrorReturnCode
else:
  from pbs import ErrorReturnCode

from clint.textui import colored

from gitless import core

from . import (
    gl_track, gl_untrack, gl_status, gl_diff, gl_commit, gl_branch, gl_tag,
    gl_checkout, gl_merge, gl_resolve, gl_fuse, gl_remote, gl_publish,
    gl_switch, gl_init, gl_history)
from . import pprint


SUCCESS = 0
ERRORS_FOUND = 1
# 2 is used by argparse to indicate cmd syntax errors.
INTERNAL_ERROR = 3
NOT_IN_GL_REPO = 4

VERSION = '0.8.5'
URL = 'http://gitless.com'


repo = None
try:
  repo = core.Repository()
  try:
    colored.DISABLE_COLOR = not repo.config.get_bool('color.ui')
  except pygit2.GitError:
    colored.DISABLE_COLOR = (
        repo.config['color.ui'] in ['no', 'never'])
except (core.NotInRepoError, KeyError):
  pass


def main():
  parser = argparse.ArgumentParser(
      description=(
          'Gitless: a version control system built on top of Git. More info, '
          'downloads and documentation available at {0}'.format(URL)),
      formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument(
      '--version', action='version', version=(
         'GL Version: {0}\nYou can check if there\'s a new version of Gitless '
         'available at {1}'.format(VERSION, URL)))
  subparsers = parser.add_subparsers(title='subcommands', dest='subcmd_name')
  subparsers.required = True

  sub_cmds = [
      gl_track, gl_untrack, gl_status, gl_diff, gl_commit, gl_branch, gl_tag,
      gl_checkout, gl_merge, gl_resolve, gl_fuse, gl_remote, gl_publish,
      gl_switch, gl_init, gl_history]
  for sub_cmd in sub_cmds:
    sub_cmd.parser(subparsers, repo)

  if len(sys.argv) == 1:
    parser.print_help()
    return SUCCESS

  args = parser.parse_args()
  try:
    if args.subcmd_name != 'init' and not repo:
      raise core.NotInRepoError('You are not in a Gitless\'s repository')

    return SUCCESS if args.func(args, repo) else ERRORS_FOUND
  except KeyboardInterrupt:
    pprint.puts('\n')
    pprint.msg('Keyboard interrupt detected, operation aborted')
    return SUCCESS
  except core.NotInRepoError as e:
    pprint.err(e)
    pprint.err_exp('do gl init to turn this directory into an empty repository')
    pprint.err_exp('do gl init remote_repo to clone an existing repository')
    return NOT_IN_GL_REPO
  except (ValueError, pygit2.GitError, core.GlError) as e:
    pprint.err(e)
    return ERRORS_FOUND
  except ErrorReturnCode as e:
    pprint.err(e.stderr)
    return ERRORS_FOUND
  except:
    pprint.err('Some internal error occurred')
    pprint.err_exp(
        'If you want to help, see {0} for info on how to report bugs and '
        'include the following information:\n\n{1}\n\n{2}'.format(
            URL, VERSION, traceback.format_exc()))
    return INTERNAL_ERROR
