import sys
import traceback

import lib


def run(main):
  if not lib.gl_dir():
    print (
        'You are not in a Gitless repository. To make this directory a '
        'repository do gl init. For cloning existing repositories do gl clone '
        'src.')
    return
  try:
    main()
  except:
    print (
        'Oops...something went wrong (recall that Gitless is in beta). If you '
        'want to give us a hand, report the bug at '
        'http://people.csail.mit.edu/sperezde/gitless/bug and copy paste the '
        'following into the form:\n\n%s' % traceback.format_exc())
