# -*- coding: utf-8 -*-
# Gitless - a version control system built on top of Git.
# Licensed under GNU GPL v2.

"""gl history - Show commit history."""


from __future__ import unicode_literals

import os
import tempfile

from clint.textui import colored

from . import helpers, pprint


def parser(subparsers):
  """Adds the history parser to the given subparsers object."""
  history_parser = subparsers.add_parser(
      'history', help='show commit history')
  history_parser.add_argument(
      '-v', '--verbose', help='be verbose, will output the diffs of the commit',
      action='store_true')
  history_parser.set_defaults(func=main)


def main(args, repo):
  curr_b = repo.current_branch
  with tempfile.NamedTemporaryFile(mode='w', delete=False) as tf:
    for ci in curr_b.history():
      merge_commit = len(ci.parent_ids) > 1
      color = colored.magenta if merge_commit else colored.yellow
      if merge_commit:
        pprint.puts(color('Merge commit'), stream=tf.write)
        merges_str = ' '.join(str(oid)[:7] for oid in ci.parent_ids)
        pprint.puts(color('Merges:    {0}'.format(merges_str)), stream=tf.write)
      pprint.commit(ci, color=color, stream=tf.write)
      pprint.puts(stream=tf.write)
      pprint.puts(stream=tf.write)
      if args.verbose and len(ci.parents) == 1:  # TODO: merge commits diffs
        for patch in curr_b.diff_commits(ci.parents[0], ci):
          pprint.diff(patch, stream=tf.write)
  helpers.page(tf.name)
  os.remove(tf.name)
  return True
