# -*- coding: utf-8 -*-
# Gitless - a version control system built on top of Git.
# Licensed under GNU GPL v2.

"""gl diff - Show changes in files."""


from __future__ import unicode_literals

import os
import subprocess
import tempfile

from gitless import core

from . import pprint


def parser(subparsers):
  """Adds the diff parser to the given subparsers object."""
  diff_parser = subparsers.add_parser(
      'diff', help='show changes in files')
  diff_parser.add_argument(
      'files', nargs='*', help='the files to diff')
  diff_parser.set_defaults(func=main)


def main(args, repo):
  curr_b = repo.current_branch
  if not args.files:
    # Tracked modified files.
    files = [
        f.fp for f in curr_b.status()
        if f.type == core.GL_STATUS_TRACKED and f.modified]
    files.sort()
    if not files:
      pprint.warn(
          'Nothing to diff (there are no tracked files with modifications)')
      return True
  else:
    files = args.files

  success = True
  for fp in files:
    try:
      patch = curr_b.diff_file(os.path.relpath(fp, repo.root))
    except KeyError:
      pprint.err('Can\'t diff non-existent file {0}'.format(fp))
      success = False
      continue

    if patch.is_binary:
      pprint.msg('Not showing diffs for binary file {0}'.format(fp))
      continue

    if (not patch.additions) and (not patch.deletions):
      pprint.warn('No diffs to output for {0}'.format(fp))
      continue

    with tempfile.NamedTemporaryFile(mode='w', delete=False) as tf:
      pprint.diff(patch, stream=tf.write)

    subprocess.call('less -r -f {0}'.format(tf.name), shell=True)
    os.remove(tf.name)

  return success
