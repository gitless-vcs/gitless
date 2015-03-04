# Gitless - a version control system built on top of Git.
# Licensed under GNU GPL v2.

"""gl diff - Show changes in files."""


import os
import subprocess
import tempfile

import gitless.core.core as core

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
    if not files:
      pprint.msg(
          'Nothing to diff (there are no tracked files with modifications).')
      return True
  else:
    files = args.files

  success = True
  for fp in files:
    try:
      out, padding, additions, deletions = curr_b.diff_file(
          os.path.relpath(fp, repo.root))
    except KeyError:
      pprint.err('Can\'t diff non-existent file {0}'.format(fp))
      success = False
      continue

    if not out:
      pprint.msg('No diffs to output for {0}'.format(fp))
      continue

    with tempfile.NamedTemporaryFile(mode='w', delete=False) as tf:
      pprint.msg(
          'Diff of file {0} with its last committed version'.format(fp),
          p=tf.write)
      put_s = lambda num: '' if num == 1 else 's'
      pprint.msg(
          '{0} line{1} added'.format(additions, put_s(additions)), p=tf.write)
      pprint.msg(
          '{0} line{1} removed'.format(deletions, put_s(deletions)),
          p=tf.write)
      pprint.diff(out, padding, p=tf.write)

    subprocess.call('less -r -f {0}'.format(tf.name), shell=True)
    os.remove(tf.name)

  return success
