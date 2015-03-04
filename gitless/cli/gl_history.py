# Gitless - a version control system built on top of Git.
# Licensed under GNU GPL v2.

"""gl history - Show commit history."""


import os
import subprocess
import tempfile

from clint.textui import colored, indent, puts

from . import pprint


def parser(subparsers):
  """Adds the history parser to the given subparsers object."""
  history_parser = subparsers.add_parser(
      'history', help='show commit history')
  history_parser.add_argument(
      '-v', '--verbose', help='be verbose, will output the diffs of the commit',
      action='store_true')
  history_parser.set_defaults(func=main)


def main(args, repo):
  with tempfile.NamedTemporaryFile(mode='w', delete=False) as tf:
    for ci in repo.current_branch.history(include_diffs=args.verbose):
      puts(colored.yellow('Commit Id: {0}'.format(ci.id)), stream=tf.write)
      puts(colored.yellow(
        'Author:    {0} <{1}>'.format(ci.author.name, ci.author.email)),
        stream=tf.write)
      puts(colored.yellow(
        'Date:      {0} ({1})'.format(ci.author.date, ci.author.date_relative)),
        stream=tf.write)
      puts(stream=tf.write)
      with indent(4):
        for l in ci.msg.splitlines():
          puts(l, stream=tf.write)
      puts(stream=tf.write)
      puts(stream=tf.write)
      for diff in ci.diffs:
        puts(
            colored.cyan('Diff of file {0}'.format(diff.fp_before)),
            stream=tf.write)
        if diff.fp_before != diff.fp_after:
          puts(colored.cyan(
              ' (renamed to {0})'.format(diff.fp_after)), stream=tf.write)
        puts(stream=tf.write)
        puts(stream=tf.write)
        out, padding, additions, deletions = diff.diff
        put_s = lambda num: '' if num == 1 else 's'
        puts(
            '{0} line{1} added'.format(additions, put_s(additions)),
            stream=tf.write)
        puts(
            '{0} line{1} removed'.format(deletions, put_s(deletions)),
            stream=tf.write)
        pprint.diff(out, padding, p=tf.write)

        puts(stream=tf.write)
        puts(stream=tf.write)
      puts(stream=tf.write)
  subprocess.call('less -r -f {0}'.format(tf.name), shell=True)
  os.remove(tf.name)
  return True
