# Gitless - a version control system built on top of Git.
# Licensed under GNU GPL v2.

"""gl publish - Publish commits upstream."""


from gitless.core import core

from . import helpers
from . import pprint


def parser(subparsers):
  """Adds the publish parser to the given subparsers object."""
  publish_parser = subparsers.add_parser(
      'publish', help='publish commits upstream')
  publish_parser.add_argument(
      'branch', nargs='?', help='the branch where to publish commits')
  publish_parser.set_defaults(func=main)


def main(args):
  repo = core.Repository()
  current_b = repo.current_branch

  dst_branch = None
  if not args.branch:
    # We use the upstream branch, if any
    if not current_b.upstream:
      pprint.err(
          'No dst branch specified and the current branch has no upstream '
          'branch set')
      return False
    dst_branch = current_b.upstream
    pprint.msg(
        'No dst branch specified, defaulted to publishing changes to upstream '
        'branch {0}'.format(helpers.get_branch_name(dst_branch)))
  else:
    dst_branch = helpers.get_branch(args.src, repo)


  print(repo.current_branch.publish(dst_branch))
  pprint.msg('Publish succeeded')
  return True
