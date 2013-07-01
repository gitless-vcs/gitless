import sys
import traceback

import lib
import pprint


SUCCESS = 0
ERRORS_FOUND = 1
# 2 is used by argsparse to indicate cmd syntax errors.
INTERNAL_ERROR = 3
NOT_IN_GL_REPO = 4


def run(main, is_init=False):
  if not is_init and not lib.gl_dir():
    pprint.err(
        'You are not in a Gitless repository. To make this directory a '
        'repository do gl init. For cloning existing repositories do gl init '
        'repo.')
    sys.exit(NOT_IN_GL_REPO)

  try:
    ret_code = main()
    sys.exit(ret_code)
  except SystemExit as se:
    # This is from argsparse, we let it go through.
    raise se
  except KeyboardInterrupt:
    # The user pressed Crl-c.
    print '\n'
    pprint.msg('Keyboard interrupt detected, operation aborted')
    sys.exit()
  except:
    pprint.err(
        'Oops...something went wrong (recall that Gitless is in beta). If you '
        'want to give us a hand, report the bug at '
        'http://people.csail.mit.edu/sperezde/gitless/bug and copy paste the '
        'following into the form:\n\n%s' % traceback.format_exc())
    sys.exit(INTERNAL_ERROR)
