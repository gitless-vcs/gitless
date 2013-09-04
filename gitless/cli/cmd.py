# Gitless - a version control system built on top of Git.
# Copyright (c) 2013  Santiago Perez De Rosso.
# Licensed under GNU GPL, version 2.

import sys
import traceback

from gitless.core import repo as repo_lib

import pprint


SUCCESS = 0
ERRORS_FOUND = 1
# 2 is used by argparse to indicate cmd syntax errors.
INTERNAL_ERROR = 3
NOT_IN_GL_REPO = 4

GL_VERSION = 'kendall.0.1'


class NotInGlDirError(Exception):
  """Exception raised when the cwd is not a Gitless dir."""


def check_gl_dir():
  if not repo_lib.gl_dir():
    raise NotInGlDirError()


def run(main):
  """Wrapper for the main function."""
  try:
    ret_code = main()
    sys.exit(ret_code)
  except SystemExit as se:
    # This is from argparse, we let it go through.
    raise se
  except KeyboardInterrupt:
    # The user pressed Crl-c.
    print '\n'
    pprint.msg('Keyboard interrupt detected, operation aborted')
    sys.exit()
  except NotInGlDirError:
    pprint.err(
        'You are not in a Gitless repository. To make this directory a '
        'repository do gl init. For cloning existing repositories do gl init '
        'repo.')
    sys.exit(NOT_IN_GL_REPO)
  except:
    pprint.err(
        'Oops...something went wrong (recall that Gitless is in beta). If you '
        'want to help, report the bug at '
        'http://people.csail.mit.edu/sperezde/gitless/community.html and '
        'include the following in the email:\n\n%s\n\n%s' %
        (GL_VERSION, traceback.format_exc()))
    sys.exit(INTERNAL_ERROR)
