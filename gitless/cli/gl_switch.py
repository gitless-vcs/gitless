# Gitless - a version control system built on top of Git.
# Licensed under GNU GPL v2.

"""gl switch - Switch branches."""


from clint.textui import colored

from gitless.core import branch as branch_lib
from gitless.core import sync as sync_lib

from . import pprint


def parser(subparsers):
  """Adds the switch parser to the given subparsers object."""
  switch_parser = subparsers.add_parser(
      'switch', help='switch branches')
  switch_parser.add_argument('branch', help='switch to branch')
  switch_parser.add_argument(
      '-mo', '--move-over',
      help='move uncomitted changes made in the current branch to the '
      'destination branch',
      action='store_true')
  switch_parser.set_defaults(func=main)


def main(args):
  b_st = branch_lib.status(args.branch)
  if not b_st:
    pprint.err('Branch {0} doesn\'t exist'.format(colored.green(args.branch)))
    pprint.err_exp('to list existing branches do gl branch')
    return False
  if b_st.is_current:
    pprint.err(
        'You are already in branch {0}. No need to switch.'.format(
              colored.green(args.branch)))
    pprint.err_exp('to list existing branches do gl branch')
    return False

  if sync_lib.rebase_in_progress():
    pprint.err(
        'You can\'t switch branches when a rebase is in progress (yet '
        '-- this will be implemented in the future)')
    return False
  elif sync_lib.merge_in_progress():
    pprint.err(
        'You can\'t switch branches when merge is in progress (yet '
        '-- this will be implemented in the future)')
    return False

  branch_lib.switch(args.branch, move_over=args.move_over)
  pprint.msg('Switched to branch {0}'.format(colored.green(args.branch)))
  return True
