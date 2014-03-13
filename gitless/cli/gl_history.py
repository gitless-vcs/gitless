# Gitless - a version control system built on top of Git.
# Copyright (c) 2013  Santiago Perez De Rosso.
# Licensed under GNU GPL, version 2.

"""gl history - Show commit history."""


import os
import subprocess
import tempfile

from gitless.core import repo as repo_lib

from . import pprint


def parser(subparsers):
  """Adds the history parser to the given subparsers object."""
  history_parser = subparsers.add_parser(
      'history', help='show commit history')
  history_parser.add_argument(
      '-v', '--verbose', help='be verbose, will output the diffs of the commit',
      action='store_true')
  history_parser.set_defaults(func=main)


def main(args):
  with tempfile.NamedTemporaryFile(mode='w', delete=False) as tf:
    for ci in repo_lib.history(include_diffs=args.verbose):
      tf.write('Commit Id: {0}\n'.format(ci.id))
      tf.write('Author:    {0} <{1}>\n'.format(ci.author.name, ci.author.email))
      tf.write('Date:      {0} ({1})\n'.format(
          ci.author.date, ci.author.date_relative))
      tf.write('\n')
      tf.write('\n'.join('   ' + l for l in ci.msg.splitlines()))
      tf.write('\n\n')
      for diff in ci.diffs:
        pprint.diff(*diff, p=tf.write)
      tf.write('\n\n')
  subprocess.call('less -r -f {0}'.format(tf.name), shell=True)
  os.remove(tf.name)
  return True
