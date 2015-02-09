# Gitless - a version control system built on top of Git.
# Licensed under GNU GPL v2.

"""gl - Main Gitless's command. Dispatcher to the other cmds."""


import argparse
import traceback


from clint.textui import colored

from gitless.core import repo as repo_lib

from . import gl_track
from . import gl_untrack
from . import gl_status
from . import gl_diff
from . import gl_commit
from . import gl_branch
from . import gl_checkout
from . import gl_merge
from . import gl_rebase
from . import gl_remote
from . import gl_resolve
from . import gl_publish
from . import gl_switch
from . import gl_init
from . import gl_history
from . import pprint


SUCCESS = 0
ERRORS_FOUND = 1
# 2 is used by argparse to indicate cmd syntax errors.
INTERNAL_ERROR = 3
NOT_IN_GL_REPO = 4

VERSION = '0.6.2'
URL = 'http://gitless.com'


colored.DISABLE_COLOR = not repo_lib.color_output()


def main():
  parser = argparse.ArgumentParser(
      description=(
          'Gitless: a version control system built on top of Git. More info, '
          'downloads and documentation available at {0}'.format(URL)),
      formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument(
      '--version', action='version', version=(
         'GL Version: {0}\nYou can check if there\'s a new version of Gitless '
         'available by visiting {1}'.format(VERSION, URL)))
  subparsers = parser.add_subparsers(dest='subcmd_name')

  sub_cmds = [
      gl_track, gl_untrack, gl_status, gl_diff, gl_commit, gl_branch,
      gl_checkout, gl_merge, gl_resolve, gl_rebase, gl_remote, gl_publish,
      gl_switch, gl_init, gl_history]
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
    # Disable pylint's superflous-parens warning (they are not superflous
    # in this case -- python 2/3 compatibility).
    # pylint: disable=C0325
    print('\n')
    pprint.msg('Keyboard interrupt detected, operation aborted')
    return SUCCESS
  except:
    pprint.err(
        'Oops...something went wrong (recall that Gitless is in beta). If you '
        'want to help, report the bug at {0}/community.html and include the '
        'following information:\n\n{1}\n\n{2}'.format(
            URL, VERSION, traceback.format_exc()))
    return INTERNAL_ERROR
