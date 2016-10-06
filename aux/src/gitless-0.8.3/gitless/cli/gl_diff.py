# -*- coding: utf-8 -*-
# Gitless - a version control system built on top of Git.
# Licensed under GNU GPL v2.

"""gl diff - Show changes in files."""


from __future__ import unicode_literals

import os
import tempfile

from . import helpers, pprint


def parser(subparsers, repo):
  """Adds the diff parser to the given subparsers object."""
  desc = 'show changes to files'
  diff_parser = subparsers.add_parser(
      'diff', help=desc, description=(
        desc.capitalize() + '. ' +
        'By default all tracked modified files are diffed. To customize the '
        ' set of files to diff use the only, exclude, and include flags'))
  helpers.oei_flags(diff_parser, repo)
  diff_parser.set_defaults(func=main)


def main(args, repo):
  files = helpers.oei_fs(args, repo)
  if not files:
    pprint.warn('No files to diff')

  success = True
  curr_b = repo.current_branch
  with tempfile.NamedTemporaryFile(mode='w', delete=False) as tf:
    for fp in files:
      try:
        patch = curr_b.diff_file(fp)
      except KeyError:
        pprint.err('Can\'t diff non-existent file {0}'.format(fp))
        success = False
        continue

      if patch.delta.is_binary:
        pprint.warn('Not showing diffs for binary file {0}'.format(fp))
        continue

      additions = patch.line_stats[1]
      deletions = patch.line_stats[2]
      if (not additions) and (not deletions):
        pprint.warn('No diffs to output for {0}'.format(fp))
        continue

      pprint.diff(patch, stream=tf.write)

  if os.path.getsize(tf.name) > 0:
    helpers.page(tf.name, repo)
  os.remove(tf.name)

  return success
